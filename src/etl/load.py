import pandas as pd
from sqlalchemy import create_engine
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
        # El parámetro 'schema' es clave aquí
        df.to_sql(table_name, engine, schema='staging', if_exists='replace', index=False)
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