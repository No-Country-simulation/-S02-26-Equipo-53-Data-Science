import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")

def validate_referential_integrity():
    """
    Verifica que todos los id_producto en ventas existan en el inventario.
    Retorna un reporte de inconsistencias.
    """
    engine = get_engine()
    
    try:
        # Cargar datos de staging para comparar
        query_ventas = "SELECT DISTINCT id_producto FROM staging.ventas_staging"
        query_inventario = "SELECT id_producto FROM staging.inventario_staging"
        
        ventas_ids = pd.read_sql(query_ventas, engine)['id_producto'].tolist()
        inventario_ids = pd.read_sql(query_inventario, engine)['id_producto'].tolist()
        
        # Encontrar IDs de productos en ventas que NO están en inventario
        missing_ids = [pid for pid in ventas_ids if pid not in inventario_ids and pid is not None]
        
        if missing_ids:
            print(f"⚠️ ADVERTENCIA: Se encontraron {len(missing_ids)} productos en ventas que no existen en inventario.")
            print(f"IDs faltantes: {missing_ids[:10]}...")
            return False, missing_ids
        
        print("✅ Integridad referencial verificada: Todos los productos existen.")
        return True, []
        
    except Exception as e:
        print(f"❌ Error durante la validación: {e}")
        return False, str(e)

if __name__ == "__main__":
    validate_referential_integrity()
