import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    """Función auxiliar para centralizar la conexión."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")

def fetch_raw_data(table_name):
    try:
        engine = get_engine()
        # Ahora le decimos a SQL que busque específicamente en el esquema 'raw'
        query = f"SELECT * FROM raw.{table_name}"
        
        df = pd.read_sql(query, engine)
        print(f"📦 Extraídos {len(df)} registros de raw.{table_name}")
        return df
    except Exception as e:
        print(f"❌ Error en la extracción de raw.{table_name}: {e}")
        raise e