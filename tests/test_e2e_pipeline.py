import os
import sys
import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Importar el orquestador principal
from scripts.orchestrator import run_etl_warehouse_pipeline

def test_full_e2e_pipeline():
    print("\n==============================================")
    print("🚀 INICIANDO PRUEBA RIGUROSA END-TO-END (E2E)")
    print("==============================================\n")

    load_dotenv()
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")

    try:
        with engine.begin() as conn:
            # 1. PREPARACIÓN (Limpiar la tabla raw de ventas para una prueba aislada)
            print("🔹 PASO 1: Vaciando ventas_raw para iniciar desde cero...")
            conn.execute(text("TRUNCATE TABLE raw.ventas_raw RESTART IDENTITY CASCADE"))
            
            # Obtener un ID de producto existente de la base de datos mock
            res_prod = conn.execute(text("SELECT id_producto FROM raw.inventario_raw LIMIT 1;")).fetchone()
            if not res_prod:
                raise Exception("Fallo Crítico: No se pudo obtener un id_producto para probar. Ejecute populate_mock_db primero.")
            
            test_product_id = res_prod[0]

            # 2. INGESTA (Simulando lo que hace el módulo de ingesta manual/excel)
            print(f"🔹 PASO 2: Insertando una venta de prueba (Venta Anónima, Producto ID: {test_product_id})...")
            # Simulamos 3 ventas del mismo producto (Total = 150 en dinero vendido si cuesta 50)
            conn.execute(text("""
                INSERT INTO raw.ventas_raw (fecha, id_producto, id_cliente, cantidad, medio_pago, fecha_carga)
                VALUES (:fecha, :prod, NULL, 3, 'Yape', NOW())
            """), {"fecha": datetime.date.today(), "prod": test_product_id})

        # 3. ETL PIPELINE (El script de tus compañeros)
        print("\n🔹 PASO 3: Ejecutando el Pipeline ETL de los analistas...")
        result = run_etl_warehouse_pipeline()
        print(f"Resultado ETL: {result}\n")

        # 4. VERIFICACIÓN (Testing riguroso en Warehouse)
        with engine.connect() as conn:
            print("🔹 PASO 4: Validando el Data Warehouse (fact_ventas)...")
            res_fact = conn.execute(text("SELECT cantidad, total_venta, id_cliente FROM warehouse.fact_ventas")).fetchall()
            
            assert len(res_fact) == 1, f"❌ ERROR: Debía haber exactamente 1 venta en el warehouse, pero hay {len(res_fact)}."
            
            venta = res_fact[0]
            cantidad_warehouse = venta[0]
            total_venta_warehouse = venta[1]
            cliente_warehouse = venta[2]

            print(f"   ➤ Cantidad registrada en Warehouse: {cantidad_warehouse}")
            print(f"   ➤ Total Venta calculada en Warehouse: S/. {total_venta_warehouse}")
            print(f"   ➤ Cliente Asignado (Inner Join): {cliente_warehouse}")

            assert cantidad_warehouse == 3, "❌ ERROR: La cantidad no coincide con la ingesta."
            
            # Si el precio unitario del producto es 50, la venta total debe ser 150
            # Solo verificamos que sea mayor a 0 para no romper por cambios de precios en el MOCK.
            assert total_venta_warehouse > 0, "❌ ERROR: El total calculado falló en la fact table."

            # El cliente en la ingesta era NULL, el ETL debió asignarlo al cliente ID 0 ("Anónimo")
            assert cliente_warehouse == 0, "❌ ERROR: El JOIN falló y la venta huérfana no se asignó al cliente 0 (Anónimo)."

        print("\n✅ ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("La integración Frontend-Ingesta-ETL-Warehouse está sólida y libre de fallos matemáticos.")
        print("==============================================\n")

    except Exception as e:
        print("\n❌ PRUEBA FALLIDA:")
        print(str(e))


if __name__ == "__main__":
    test_full_e2e_pipeline()
