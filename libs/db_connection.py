import os
import psycopg2
from dotenv import load_dotenv
from libs.logger import logError # We will move logger to libs too

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
