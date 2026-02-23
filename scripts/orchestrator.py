from scripts.etl.extract import fetch_raw_data
from scripts.etl.transform import clean_dataframe
from scripts.etl.load import upload_to_staging

def run_backend_cleaning_pipeline():
    """
    Backend Orchestrator que limpia las 3 entidades: Ventas, Inventario y Clientes.
    """
    try:
        # Definimos el mapa de qué tabla RAW va a qué tabla STAGING
        tablas_a_procesar = {
            "ventas_raw": "ventas_staging",
            "inventario_raw": "inventario_staging",
            "clientes_raw": "clientes_staging"
        }

        for raw_table, staging_table in tablas_a_procesar.items():
            # 1. EXTRAER (Ahora dinámico)
            df_raw = fetch_raw_data(raw_table)
            
            # 2. TRANSFORMAR (Tu lógica de limpieza)
            df_clean = clean_dataframe(df_raw)
            
            # 3. CARGAR (Hacia Staging)
            upload_to_staging(df_clean, staging_table)

        return {"status": "success", "message": "Proceso ETL completado para todas las tablas."}

    except Exception as e:
        return {"status": "error", "message": str(e)}