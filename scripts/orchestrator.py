from scripts.etl.extract import fetch_raw_data
from scripts.etl.transform import clean_dataframe
from scripts.etl.load import upload_to_staging
from scripts.etl.warehouse import run_warehouse

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
            
       
        # 4. VALIDACIÓN DE CALIDAD (Integridad Referencial)
        from scripts.etl.validation import validate_referential_integrity
        success, details = validate_referential_integrity()
        
        if not success:
            return {"status": "warning", "message": "ETL cargado pero con inconsistencias de datos.", "details": details}

        return {"status": "success", "message": "Proceso ETL completado y validado exitosamente."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
if __name__ == "__main__":
    print("🚀 Iniciando proceso ETL...")
    result = run_backend_cleaning_pipeline()
    print("📊 Resultado:")
    
    # cargar a warehouse
    run_warehouse()

    print(result)    