import os
from psycopg2 import sql
import datetime
from libs.db_connection import get_db_connection
from libs.logger import logInfo, logError
import pandas as pd

try:
    from thefuzz import process
except ImportError:
    process = None
    logError("Falta instalar thefuzz y python-Levenshtein para Fuzzy Matching avanzado.")

def check_product_ambiguity(cursor, schema, product_name):
    """
    Verifica si un nombre de producto tiene múltiples variantes (talla/color) activas.
    Retorna (es_ambiguo, lista_variantes)
    """
    if not product_name:
        return False, []
        
    query = sql.SQL('''
        SELECT id_producto, talla, color, stock_actual 
        FROM {}.inventario_raw 
        WHERE producto ILIKE %s AND stock_actual > 0
    ''').format(sql.Identifier(schema))
    
    cursor.execute(query, (product_name.strip(),))
    rows = cursor.fetchall()
    
    if len(rows) > 1:
        return True, [{"id": r[0], "talla": r[1], "color": r[2], "stock": r[3]} for r in rows]
    return False, []

def get_product_id(cursor, schema, product_name, talla=None, color=None):
    """
    Busca el ID del producto en inventario_raw. 
    Lógica determinista: 
    1. Coincidencia exacta (Nombre + Talla + Color)
    2. Coincidencia por Nombre + Talla (si color es nulo)
    3. Coincidencia solo por Nombre (si no hay más datos)
    """
    if not product_name:
        return None
    
    product_name = product_name.strip()
    t_val = str(talla).strip() if talla and not pd.isna(talla) else None
    c_val = str(color).strip() if color and not pd.isna(color) else None

    # Caso 1: Todo especificado
    if t_val and c_val:
        query = sql.SQL("SELECT id_producto FROM {}.inventario_raw WHERE producto ILIKE %s AND talla ILIKE %s AND color ILIKE %s LIMIT 1").format(sql.Identifier(schema))
        cursor.execute(query, (product_name, t_val, c_val))
        res = cursor.fetchone()
        if res: return res[0]

    # Caso 2: Nombre + Talla
    if t_val:
        query = sql.SQL("SELECT id_producto FROM {}.inventario_raw WHERE producto ILIKE %s AND talla ILIKE %s LIMIT 1").format(sql.Identifier(schema))
        cursor.execute(query, (product_name, t_val))
        res = cursor.fetchone()
        if res: return res[0]

    # Caso 3: Solo Nombre (Fallback final)
    query = sql.SQL("SELECT id_producto FROM {}.inventario_raw WHERE producto ILIKE %s LIMIT 1").format(sql.Identifier(schema))
    cursor.execute(query, (product_name,))
    res = cursor.fetchone()
    return res[0] if res else None

def get_product_details(cursor, schema, product_name, talla=None, color=None):
    """
    Busca los detalles completos del producto (ID, Precio, Categoria).
    Lógica determinista al igual que get_product_id.
    """
    if not product_name:
        return None
    
    product_name = product_name.strip()
    t_val = str(talla).strip() if talla and not pd.isna(talla) else None
    c_val = str(color).strip() if color and not pd.isna(color) else None
    
    campos = "id_producto, precio_venta_unitario, categoria, talla, color"

    # Caso 1: Todo especificado
    if t_val and c_val:
        query = sql.SQL(f"SELECT {campos} FROM {{}}.inventario_raw WHERE producto ILIKE %s AND talla ILIKE %s AND color ILIKE %s LIMIT 1").format(sql.Identifier(schema))
        cursor.execute(query, (product_name, t_val, c_val))
        res = cursor.fetchone()
        if res: return {"id": res[0], "precio": res[1], "categoria": res[2], "talla": res[3], "color": res[4]}

    # Caso 2: Nombre + Talla
    if t_val:
        query = sql.SQL(f"SELECT {campos} FROM {{}}.inventario_raw WHERE producto ILIKE %s AND talla ILIKE %s LIMIT 1").format(sql.Identifier(schema))
        cursor.execute(query, (product_name, t_val))
        res = cursor.fetchone()
        if res: return {"id": res[0], "precio": res[1], "categoria": res[2], "talla": res[3], "color": res[4]}

    # Caso 3: Solo Nombre
    query = sql.SQL(f"SELECT {campos} FROM {{}}.inventario_raw WHERE producto ILIKE %s LIMIT 1").format(sql.Identifier(schema))
    cursor.execute(query, (product_name,))
    res = cursor.fetchone()
    if res: return {"id": res[0], "precio": res[1], "categoria": res[2], "talla": res[3], "color": res[4]}
    
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
                
            # 2. Lógica Híbrida: Substring Match + Fuzzy Match
            dictated_lower = dictated_name.lower().strip()
            
            # Primero buscamos coincidencias directas por substring (Ej: "Polo" en "Polo Algodón Premium")
            substring_matches = []
            for p in productos_unicos:
                if dictated_lower in p.lower():
                    # Le damos score alto artificialmente (ej. 90) a las coincidencias directas
                    substring_matches.append((p, 90))
                    
            # Luego buscamos aproximaciones fonéticas/tipeo con thefuzz (Score bajado de 50 a 40 para ser más tolerante)
            fuzzy_matches = process.extractBests(dictated_name, productos_unicos, limit=limit, score_cutoff=40)
            
            # Combinamos ambos sets de resultados sin duplicados
            combined_matches_dict = {}
            for name, score in (substring_matches + (fuzzy_matches or [])):
                # Si el producto ya está en el diccionario, nos quedamos con el score más alto
                if name not in combined_matches_dict or score > combined_matches_dict[name]:
                    combined_matches_dict[name] = score
                    
            # Ordenamos por score descendente y aplicamos el límite
            mejores_matches = sorted(combined_matches_dict.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            if not mejores_matches:
                return []
                
            resultados_completos = []
            
            # 3. Por cada match rescatado, traer sus variantes reales de la BD
            for match_name, score in mejores_matches:
                query_variantes = sql.SQL('''
                    SELECT id_producto, talla, color, precio_venta_unitario, stock_actual, categoria 
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
                        "stock_actual": int(v[4]),
                        "categoria": v[5]
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
    Maneja transacciones con validación estricta de inventario.
    """
    if not sales_data:
        return {"success": False, "message": "No hay datos para guardar."}

    conn = get_db_connection()
    if not conn:
        return {"success": False, "message": "Error de conexión a base de datos."}

    schema = os.getenv("DB_SCHEMA", "public")
    inserted_count = 0
    failed_items = []
    
    try:
        # Usamos transacción atómica
        with conn:
            with conn.cursor() as cursor:
                for idx, sale in enumerate(sales_data):
                    prod_name = sale.get("producto") or "Desconocido"
                    
                    # 1. Resolver IDs referencias
                    id_producto = sale.get("id_producto_directo")
                    if not id_producto:
                        id_producto = get_product_id(cursor, schema, prod_name, sale.get("talla"), sale.get("color"))
                    
                    # VALIDACIÓN CRÍTICA: Existencia de Producto
                    if not id_producto:
                        failed_items.append({
                            "index": idx,
                            "producto": prod_name,
                            "razon": "Producto no existe en el inventario oficial."
                        })
                        continue

                    # 2. Rebajar Stock y Validar Cantidad
                    cantidad = int(sale.get("cantidad", 1))

                    query_stock = sql.SQL("""
                        UPDATE {}.inventario_raw 
                        SET stock_actual = stock_actual - %s 
                        WHERE id_producto = %s AND stock_actual >= %s
                    """).format(sql.Identifier(schema))
                    
                    cursor.execute(query_stock, (cantidad, id_producto, cantidad))
                    
                    # VALIDACIÓN CRÍTICA: Stock Insuficiente
                    if cursor.rowcount == 0:
                        failed_items.append({
                            "index": idx,
                            "producto": prod_name,
                            "razon": f"Stock insuficiente (Solicitado: {cantidad})."
                        })
                        continue

                    # 3. Insertar Venta
                    id_cliente = get_client_id(cursor, schema, sale.get("nombre_cliente"))
                    
                    query_sale = sql.SQL("""
                        INSERT INTO {}.ventas_raw 
                        (fecha, id_producto, id_cliente, cantidad, medio_pago, fecha_carga)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                    """).format(sql.Identifier(schema))
                    
                    fecha_venta = sale.get("fecha_registro")
                    if not fecha_venta:
                        fecha_venta = datetime.date.today()
                        
                    cursor.execute(query_sale, (
                        fecha_venta,
                        id_producto,
                        id_cliente,
                        cantidad,
                        sale.get("medio_pago", "Efectivo")
                    ))
                    
                    inserted_count += 1

                # Si hubo fallos, lanzamos excepción para hacer rollback de TODO
                # (Opcional: Podríamos permitir éxito parcial si el usuario lo prefiere, 
                # pero por seguridad de "protección tal cual", rollback total es mejor).
                if failed_items:
                    raise ValueError(f"Validación fallida para {len(failed_items)} items.")
                    
        return {"success": True, "message": f"Se insertaron {inserted_count} registros correctamente."}

    except ValueError as e:
        conn.rollback()
        return {
            "success": False, 
            "message": "Error de validación: Algunos productos no tienen stock o no existen.",
            "failed_items": failed_items
        }
    except Exception as e:
        if conn: conn.rollback()
        logError(f"Error general en transacción de ventas: {e}")
        return {"success": False, "message": f"Error crítico en BD: {e}"}
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
                SELECT id_producto, talla, color, stock_actual, precio_venta_unitario, categoria
                FROM {}.inventario_raw
                WHERE producto = %s AND stock_actual > 0
            ''').format(sql.Identifier(schema))
            cursor.execute(query, (product_name,))
            res = cursor.fetchall()
            return [{"id_producto": r[0], "talla": r[1], "color": r[2], "stock_actual": r[3], "precio": float(r[4]) if r[4] else 0.0, "categoria": r[5]} for r in res]
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
                return {"success": True, "id_cliente": new_id, "message": "Cliente guardado exitosamente."}
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
        return {"success": False, "message": "Error de conexión a la base de datos."}
        
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
                        # Existe, sumar stock y actualizar precios
                        query_upd = sql.SQL('''
                            UPDATE {}.inventario_raw 
                            SET stock_actual = stock_actual + %s,
                                precio_adquisicion = CASE WHEN %s > 0 THEN %s ELSE precio_adquisicion END,
                                precio_venta_unitario = CASE WHEN %s > 0 THEN %s ELSE precio_venta_unitario END,
                                fecha_carga = CURRENT_TIMESTAMP
                            WHERE id_producto = %s
                        ''').format(sql.Identifier(schema))
                        cursor.execute(query_upd, (stock, precio_adq, precio_adq, precio_ven, precio_ven, id_prod_existente))
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
                        
        return {"success": True, "message": f"Carga Exitosa: {inserted} productos nuevos creados, {updated} actualizados."}
    except Exception as e:
        conn.rollback()
        logError(f"Error en carga masiva de inventario: {e}")
        return {"success": False, "message": f"Error en BD: {e}"}
    finally:
        conn.close()
