import sys
import os
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.db_connection import get_engine
from scripts.populate_mock_db import recreate_mock_data
from scripts.orchestrator import run_etl_warehouse_pipeline

def init_remote_db():
    print("Iniciando conexión a base de datos remota...")
    engine = get_engine()
    
    with engine.begin() as conn:
        print("1. Ejecutando db_model.sql para construir todos los esquemas (raw, staging, warehouse)...")
        sql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db_model.sql'))
        with open(sql_path, "r", encoding="utf-8") as file:
            sql_script = file.read()
            # Dividir sentencias por ';' para evitar errores de múltiples sentencias
            # Aunque SQLAlchemy soporta texto libre en DBAPI
            conn.execute(text(sql_script))
    
    print("Esperando 2 segundos para sincronización...")
    time.sleep(2)
    
    print("2. Ejecutando scripts/populate_mock_db.py para llenar la zona RAW con datos de prueba...")
    recreate_mock_data()
    
    print("3. Ejecutando el ETL Pipeline para transformar desde RAW y llenar WAREHOUSE...")
    result = run_etl_warehouse_pipeline()
    print("Resultado del ETL:", result)
    
    print("Inicialización Remota Completada ✅")

if __name__ == "__main__":
    init_remote_db()
