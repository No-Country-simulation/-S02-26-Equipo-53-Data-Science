import os
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
from libs.logger import logError

load_dotenv()

def get_engine():
    """Establece conexión y devuelve un Engine de SQLAlchemy."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "postgres")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "")
    
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    try:
        # pool_pre_ping asegura que la conexion no este muerta
        engine = create_engine(url, pool_pre_ping=True)
        return engine
    except Exception as e:
        logError(f"Error creando engine SQLAlchemy: {e}")
        return None

def get_db_connection():
    """Establece conexión a la base de datos usando variables de entorno (Legacy psycopg2)."""
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
        logError(f"Error conectando a BD (psycopg2): {e}")
        return None
