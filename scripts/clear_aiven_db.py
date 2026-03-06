import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from libs.db_connection import get_db_connection
from psycopg2 import sql

def clear_db():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos de Aiven.")
        return
        
    schema = os.getenv("DB_SCHEMA", "raw")
    try:
        with conn.cursor() as cur:
            print(f"⚠️ Conectado a la base de datos. Vaciando tablas en el esquema: {schema}...")
            # CASCADE borrará también las dependencias si las hubiera y RESTART IDENTITY reinicia los contadores ID a 1
            query = sql.SQL("TRUNCATE TABLE {}.ventas_raw, {}.inventario_raw, {}.clientes_raw RESTART IDENTITY CASCADE").format(
                sql.Identifier(schema), sql.Identifier(schema), sql.Identifier(schema)
            )
            cur.execute(query)
            conn.commit()
            print("✅ ¡Tablas de Ventas, Inventario y Clientes vaciadas completamente y listas para usar desde cero!")
    except Exception as e:
        print(f"❌ Error crítico al limpiar la base de datos: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    clear_db()
