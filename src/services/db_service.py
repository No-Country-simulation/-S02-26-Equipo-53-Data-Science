
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from src.utils.logger import logInfo, logError
import datetime

load_dotenv()

def get_db_connection():
    """Establece conexión a la base de datos usando variables de entorno."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        return conn
    except Exception as e:
        logError(f"Error conectando a BD: {e}")
        return None

def get_product_id(cursor, schema, product_name):
    """
    Busca el ID del producto en inventario_raw. 
    Solo lectura. Retorna None si no existe.
    """
    if not product_name:
        return None
    
    product_name = product_name.strip()
    
    # Solo buscar
    query_search = sql.SQL("SELECT id_producto FROM {}.inventario_raw WHERE producto ILIKE %s").format(sql.Identifier(schema))
    cursor.execute(query_search, (product_name,))
    res = cursor.fetchone()
    if res:
        return res[0]
    return None

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
                    # 1. Resolver IDs referencias (Solo lectura)
                    # Si no existen, serán None (NULL en la BD)
                    id_producto = get_product_id(cursor, schema, sale.get("producto"))
                    id_cliente = get_client_id(cursor, schema, sale.get("nombre_cliente"))
                    
                    if not id_producto:
                         # Loguear advertencia pero intentar insertar igual (puede que la BD permita NULL o tenga trigger)
                         # OJO: Si la columna es NOT NULL y no tiene default, esto fallará.
                         # Para efectos de la demo, intentamos.
                         logInfo(f"Advertencia: Producto '{sale.get('producto')}' no encontrado. Se insertará con ID NULL o 0 si es posible.")
                    
                    # 2. Insertar Venta
                    # Schema ventas_raw: id_venta, fecha, id_producto, id_cliente, cantidad, talla, color, precio_venta_unitario, medio_pago, fecha_carga
                    query_sale = sql.SQL("""
                        INSERT INTO {}.ventas_raw 
                        (fecha, id_producto, id_cliente, cantidad, talla, color, precio_venta_unitario, medio_pago, fecha_carga)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
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
                        sale.get("talla"),
                        sale.get("color"),
                        sale.get("precio", 0.0),
                        sale.get("medio_pago", "Efectivo")
                    ))
                    inserted_count += 1
                    
        return {"success": True, "message": f"Se insertaron {inserted_count} registros correctamente."}

    except Exception as e:
        conn.rollback()
        logError(f"Error general en transacción de ventas: {e}")
        return {"success": False, "message": f"Error al guardar en BD: {e}"}
    finally:
        conn.close()
