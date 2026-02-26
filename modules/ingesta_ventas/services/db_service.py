import os
from psycopg2 import sql
import datetime
from libs.db_connection import get_db_connection
from libs.logger import logInfo, logError

try:
    from thefuzz import process
except ImportError:
    process = None
    logError("Falta instalar thefuzz y python-Levenshtein para Fuzzy Matching avanzado.")

def get_product_id(cursor, schema, product_name, talla=None, color=None):
    """
    Busca el ID del producto en inventario_raw. 
    Solo lectura. Retorna None si no existe.
    """
    if not product_name:
        return None
    
    product_name = product_name.strip()
    
    # Intentar buscar coincidencia exacta con talla y color si se proporcionan
    conditions = ["producto ILIKE %s"]
    params = [product_name]
    
    if talla and str(talla).strip() and str(talla).strip().lower() != "única":
        conditions.append("talla ILIKE %s")
        params.append(str(talla).strip())
        
    if color and str(color).strip() and str(color).strip().lower() != "único":
        conditions.append("color ILIKE %s")
        params.append(str(color).strip())
        
    where_clause = " AND ".join(conditions)
    
    query_exact = sql.SQL(f"SELECT id_producto FROM {{}}.inventario_raw WHERE {where_clause} LIMIT 1").format(sql.Identifier(schema))
    cursor.execute(query_exact, tuple(params))
    res = cursor.fetchone()
    if res:
        return res[0]
        
    # Fallback solo por nombre (por si la variante no fue especificada correctamente)
    query_search = sql.SQL("SELECT id_producto FROM {}.inventario_raw WHERE producto ILIKE %s LIMIT 1").format(sql.Identifier(schema))
    cursor.execute(query_search, (product_name,))
    res_fallback = cursor.fetchone()
    if res_fallback:
        return res_fallback[0]
        
    return None

def search_inventory_fuzzy(dictated_name: str, limit: int = 5) -> list:
    """
    Busca el mejor match posible en la tabla inventario_raw usando thefuzz.
    Descarga los nombres únicos de inventario_raw y hace un fuzzy match.
    Retorna una lista de diccionarios con las variantes disponibles de los productos más parecidos.
    
    Estructura de retorno:
    [
      {
         "producto_oficial": "Polo Deportivo",
         "score": 90,
         "variantes": [
             {"id_producto": 1, "talla": "S", "color": "Rojo", "precio": 50.0},
             ...
         ]
      },
      ...
    ]
    """
    if not dictated_name or not process:
        return []
        
    conn = get_db_connection()
    if not conn:
        logError("No db connection para fuzzy search")
        return []
        
    schema = os.getenv("DB_SCHEMA", "public")
    
    try:
        with conn.cursor() as cursor:
            # 1. Obtener todos los productos únicos del inventario para hacer el thefuzz
            query_distinct = sql.SQL('''
                SELECT DISTINCT producto 
                FROM {}.inventario_raw 
                WHERE stock_actual > 0
            ''').format(sql.Identifier(schema))
            
            cursor.execute(query_distinct)
            productos_unicos = [row[0] for row in cursor.fetchall() if row[0]]
            
            if not productos_unicos:
                return []
                
            # 2. Hacer Fuzzy Match. Extract_Bests devuelve (nombre, score)
            mejores_matches = process.extractBests(dictated_name, productos_unicos, limit=limit, score_cutoff=60)
            
            if not mejores_matches:
                return []
                
            resultados_completos = []
            
            # 3. Por cada match rescatado, traer sus variantes reales de la BD
            for match_name, score in mejores_matches:
                query_variantes = sql.SQL('''
                    SELECT id_producto, talla, color, precio_venta_unitario, stock_actual 
                    FROM {}.inventario_raw
                    WHERE producto = %s AND stock_actual > 0
                ''').format(sql.Identifier(schema))
                cursor.execute(query_variantes, (match_name,))
                variantes_rows = cursor.fetchall()
                
                variantes = []
                for v in variantes_rows:
                    variantes.append({
                        "id_producto": v[0],
                        "talla": v[1],
                        "color": v[2],
                        "precio": float(v[3]) if v[3] else 0.0,
                        "stock_actual": int(v[4])
                    })
                    
                resultados_completos.append({
                    "producto_oficial": match_name,
                    "score": score,
                    "variantes": variantes
                })
                
            return resultados_completos
            
    except Exception as e:
        logError(f"Error en search_inventory_fuzzy: {e}")
        return []
    finally:
        conn.close()

def get_client_id(cursor, schema, client_name):
    """
    Busca ID cliente en clientes_raw. 
    Solo lectura. Retorna None si no existe.
    """
    if not client_name or client_name == "Anónimo":
        return None 
        
    client_name = client_name.strip()
    
    # Solo buscar
    query_search = sql.SQL("SELECT id_cliente FROM {}.clientes_raw WHERE nombre_cliente ILIKE %s").format(sql.Identifier(schema))
    cursor.execute(query_search, (client_name,))
    res = cursor.fetchone()
    if res:
        return res[0]
    return None

def insert_sales_to_db(sales_data):
    """
    Recibe lista de diccionarios de ventas y los inserta en ventas_raw.
    Maneja transacciones.
    """
    if not sales_data:
        return {"success": False, "message": "No hay datos para guardar."}

    conn = get_db_connection()
    if not conn:
        return {"success": False, "message": "Error de conexión a base de datos."}

    schema = os.getenv("DB_SCHEMA", "public")
    inserted_count = 0
    
    try:
        with conn:
            with conn.cursor() as cursor:
                for sale in sales_data:
                    # 1. Resolver IDs referencias
                    # Si viene id_producto_directo (fuerza de UI), lo usamos directo.
                    # Sino, intentamos resolver por texto (flujo bulk legacy).
                    if sale.get("id_producto_directo"):
                        id_producto = sale.get("id_producto_directo")
                    else:
                        id_producto = get_product_id(cursor, schema, sale.get("producto"), sale.get("talla"), sale.get("color"))
                        
                    id_cliente = get_client_id(cursor, schema, sale.get("nombre_cliente"))
                    
                    if not id_producto:
                         # Loguear advertencia pero intentar insertar igual (puede que la BD permita NULL o tenga trigger)
                         # OJO: Si la columna es NOT NULL y no tiene default, esto fallará.
                         # Para efectos de la demo, intentamos.
                         logInfo(f"Advertencia: Producto '{sale.get('producto')}' no encontrado. Se insertará con ID NULL o 0 si es posible.")
                    
                    # 2. Insertar Venta
                    # Schema ventas_raw: id_venta, fecha, id_producto, id_cliente, cantidad, medio_pago, fecha_carga
                    query_sale = sql.SQL("""
                        INSERT INTO {}.ventas_raw 
                        (fecha, id_producto, id_cliente, cantidad, medio_pago, fecha_carga)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                    """).format(sql.Identifier(schema))
                    
                    # Formatear fecha si es string
                    fecha_venta = sale.get("fecha_registro")
                    if not fecha_venta:
                        fecha_venta = datetime.date.today()
                        
                    cursor.execute(query_sale, (
                        fecha_venta,
                        id_producto, # Puede ser None
                        id_cliente,  # Puede ser None
                        sale.get("cantidad", 1),
                        sale.get("medio_pago", "Efectivo")
                    ))
                    
                    # 3. Rebajar Stock Automáticamente
                    if id_producto:
                        query_stock = sql.SQL("""
                            UPDATE {}.inventario_raw 
                            SET stock_actual = stock_actual - %s 
                            WHERE id_producto = %s AND stock_actual >= %s
                        """).format(sql.Identifier(schema))
                        cursor.execute(query_stock, (sale.get("cantidad", 1), id_producto, sale.get("cantidad", 1)))
                        
                    inserted_count += 1
                    
        return {"success": True, "message": f"Se insertaron {inserted_count} registros correctamente."}

    except Exception as e:
        conn.rollback()
        logError(f"Error general en transacción de ventas: {e}")
        return {"success": False, "message": f"Error al guardar en BD: {e}"}
    finally:
        conn.close()

def get_inventory_summary():
    """
    Obtiene un resumen de productos agrupados del inventario.
    """
    conn = get_db_connection()
    if not conn:
        return []
    schema = os.getenv("DB_SCHEMA", "public")
    try:
        with conn.cursor() as cursor:
            # Agrupar por producto y categoria
            query = sql.SQL('''
                SELECT producto, categoria, SUM(stock_actual) as total_stock
                FROM {}.inventario_raw
                GROUP BY producto, categoria
                HAVING SUM(stock_actual) > 0
                ORDER BY producto
            ''').format(sql.Identifier(schema))
            cursor.execute(query)
            res = cursor.fetchall()
            return [{"producto": r[0], "categoria": r[1], "total_stock": r[2]} for r in res]
    except Exception as e:
        logError(f"Error en get_inventory_summary: {e}")
        return []
    finally:
        conn.close()

def get_product_variants(product_name):
    """
    Obtiene las variantes (talla, color) de un producto específico.
    """
    conn = get_db_connection()
    if not conn:
        return []
    schema = os.getenv("DB_SCHEMA", "public")
    try:
        with conn.cursor() as cursor:
            query = sql.SQL('''
                SELECT talla, color, stock_actual, precio_venta_unitario
                FROM {}.inventario_raw
                WHERE producto = %s AND stock_actual > 0
            ''').format(sql.Identifier(schema))
            cursor.execute(query, (product_name,))
            res = cursor.fetchall()
            return [{"talla": r[0], "color": r[1], "stock_actual": r[2], "precio_venta_unitario": r[3]} for r in res]
    except Exception as e:
        logError(f"Error en get_product_variants: {e}")
        return []
    finally:
        conn.close()

def get_all_clients():
    """
    Lista a todos los clientes.
    """
    conn = get_db_connection()
    if not conn:
        return []
    schema = os.getenv("DB_SCHEMA", "public")
    try:
        with conn.cursor() as cursor:
            query = sql.SQL('''
                SELECT id_cliente, nombre_cliente, ubicacion_cliente, genero
                FROM {}.clientes_raw
                ORDER BY nombre_cliente
            ''').format(sql.Identifier(schema))
            cursor.execute(query)
            res = cursor.fetchall()
            return [{"id_cliente": r[0], "nombre_cliente": r[1], "ubicacion_cliente": r[2], "genero": r[3]} for r in res]
    except Exception as e:
        logError(f"Error en get_all_clients: {e}")
        return []
    finally:
        conn.close()

def insert_new_client(client_data):
    """
    Inserta un nuevo cliente en la BD.
    """
    conn = get_db_connection()
    if not conn:
        return {"success": False, "message": "No DB connection"}
    schema = os.getenv("DB_SCHEMA", "public")
    try:
        with conn:
            with conn.cursor() as cursor:
                query = sql.SQL('''
                    INSERT INTO {}.clientes_raw 
                    (nombre_cliente, ubicacion_cliente, genero, fecha_registro, fecha_carga)
                    VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_TIMESTAMP)
                    RETURNING id_cliente
                ''').format(sql.Identifier(schema))
                cursor.execute(query, (
                    client_data.get("nombre_cliente"),
                    client_data.get("ubicacion_cliente"),
                    client_data.get("genero")
                ))
                new_id = cursor.fetchone()[0]
                return {"success": True, "id_cliente": new_id, "message": "Cliente guardado"}
    except Exception as e:
        conn.rollback()
        logError(f"Error insertando cliente: {e}")
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def upsert_inventory_bulk(inventory_data: list):
    """
    Inserta o actualiza masivamente el inventario.
    Busca por (producto, talla, color). Si existe, suma stock. Si no, inserta.
    """
    if not inventory_data:
        return {"success": False, "message": "No hay datos de inventario."}
        
    conn = get_db_connection()
    if not conn:
        return {"success": False, "message": "No DB connection"}
        
    schema = os.getenv("DB_SCHEMA", "public")
    inserted, updated = 0, 0
    
    try:
        with conn:
            with conn.cursor() as cursor:
                for item in inventory_data:
                    prod = item.get("producto")
                    talla = item.get("talla")
                    color = item.get("color")
                    stock = int(item.get("stock_actual", 0))
                    precio_adq = float(item.get("precio_adquisicion", 0.0))
                    precio_ven = float(item.get("precio_venta", 0.0))
                    categoria = item.get("categoria", "Sin Categoría")
                    
                    # Verificar si existe variante
                    id_prod_existente = get_product_id(cursor, schema, prod, talla, color)
                    
                    if id_prod_existente:
                        # Existe, sumar stock
                        query_upd = sql.SQL('''
                            UPDATE {}.inventario_raw 
                            SET stock_actual = stock_actual + %s,
                                precio_adquisicion = %s,
                                precio_venta_unitario = %s,
                                fecha_carga = CURRENT_TIMESTAMP
                            WHERE id_producto = %s
                        ''').format(sql.Identifier(schema))
                        cursor.execute(query_upd, (stock, precio_adq, precio_ven, id_prod_existente))
                        updated += 1
                    else:
                        # Insertar nuevo
                        query_ins = sql.SQL('''
                            INSERT INTO {}.inventario_raw 
                            (producto, categoria, talla, color, stock_actual, precio_adquisicion, precio_venta_unitario, fecha_carga)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ''').format(sql.Identifier(schema))
                        cursor.execute(query_ins, (
                            prod, categoria, talla, color, stock, precio_adq, precio_ven
                        ))
                        inserted += 1
                        
        return {"success": True, "message": f"Inventario: {inserted} nuevos, {updated} actualizados."}
    except Exception as e:
        conn.rollback()
        logError(f"Error en carga masiva de inventario: {e}")
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def resolve_and_insert_sales_bulk(sales_data: list):
    """
    Inserta ventas resolviendo o creando clientes al vuelo.
    Llama internamente a insert_sales_to_db pasando los diccionarios limpios.
    La principal diferencia aquí es que si un cliente no existe, lo fuerza a crear
    antes de delegarlo a la funcion principal de grabacion de ventas.
    """
    if not sales_data:
         return {"success": False, "message": "No hay ventas"}
         
    conn = get_db_connection()
    if not conn:
        return {"success": False, "message": "No DB connection"}
        
    schema = os.getenv("DB_SCHEMA", "public")
    
    # Pre-procesar resolucion de clientes
    try:
        with conn:
            with conn.cursor() as cursor:
                # Cache local para no golpear BD 100 veces por el mismo cliente
                nombres_resueltos = {}
                
                for sale in sales_data:
                    cname = sale.get("nombre_cliente", "Anónimo")
                    
                    if cname not in nombres_resueltos:
                        idc = get_client_id(cursor, schema, cname)
                        if not idc and cname != "Anónimo":
                             # Crear cliente si no existe
                             query_c = sql.SQL('''
                                INSERT INTO {}.clientes_raw (nombre_cliente, ubicacion_cliente, genero, fecha_registro, fecha_carga)
                                VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_TIMESTAMP) RETURNING id_cliente
                             ''').format(sql.Identifier(schema))
                             cursor.execute(query_c, (cname, "Desconocido", "U"))
                             idc = cursor.fetchone()[0]
                             
                        nombres_resueltos[cname] = idc
                        
        # Luego de pre-resolver/crear clientes, usamos la funcion de venta estándar 
        # (la cual reutilizará las conexiones y hará su propio commit y rebaja de stock)
        return insert_sales_to_db(sales_data)
        
    except Exception as e:
         logError(f"Error resolviendo entidades en bulk ventas: {e}")
         return {"success": False, "message": f"Error cruzando datos: {e}"}
    finally:
         conn.close()
