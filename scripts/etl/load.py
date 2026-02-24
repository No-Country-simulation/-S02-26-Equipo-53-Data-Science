import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    """Crea la conexión a Aiven."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")

def upload_to_staging(df, table_name):
    try:
        engine = get_engine()
        # Usamos una transacción para vaciar e insertar (Estrategia sugerida)
        with engine.begin() as conn:
            # 1. Vaciar la tabla (Truncate) - mucho más seguro que 'replace'
            conn.execute(text(f"TRUNCATE TABLE staging.{table_name}"))
            
            # 2. Insertar los nuevos datos (Append)
            df.to_sql(table_name, conn, schema='staging', if_exists='append', index=False)
            
        print(f"✅ Datos cargados exitosamente en staging.{table_name}")
        return True
    except Exception as e:
        print(f"❌ Error al cargar en staging.{table_name}: {e}")
        return False

# Opcional: Funciones directas para mayor claridad en el orquestador
def cargar_ventas_staging(df):
    return upload_to_staging(df, 'ventas_staging')

def cargar_inventario_staging(df):
    return upload_to_staging(df, 'inventario_staging')

def cargar_clientes_staging(df):
    return upload_to_staging(df, 'clientes_staging')