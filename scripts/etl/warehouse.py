from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
# Cargar variables de entorno
load_dotenv()

def get_engine():
    """Función auxiliar para centralizar la conexión."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
# ==========================
# 🔹 CONFIGURACIÓN DB
# ==========================


# ==========================
# 🔹 TRUNCATE WAREHOUSE
# ==========================

def truncate_warehouse(engine):
    print("🧹 Limpiando tablas WAREHOUSE...")

    query = """
    TRUNCATE TABLE 
        warehouse.fact_ventas,
        warehouse.fact_inventario,
        warehouse.dim_medio_pago,
        warehouse.dim_cliente,
        warehouse.dim_producto,
        warehouse.dim_fecha
    RESTART IDENTITY CASCADE;
    """

    with engine.begin() as conn:
        conn.execute(text(query))

    print("✔ Warehouse limpio correctamente\n")


# ==========================
# 🔹 CARGA DIMENSIONES
# ==========================

def load_dimensions(engine):
    print("📊 Cargando dimensiones...")

    queries = [

        # 📅 DIM_FECHA
        """
        INSERT INTO warehouse.dim_fecha (id_fecha, anio, mes, dia, nombre_mes, dia_semana)
        SELECT DISTINCT
            fecha_base,
            EXTRACT(YEAR FROM fecha_base),
            EXTRACT(MONTH FROM fecha_base),
            EXTRACT(DAY FROM fecha_base),
            TRIM(TO_CHAR(fecha_base, 'Month')),
            TRIM(TO_CHAR(fecha_base, 'Day'))
        FROM (
            SELECT DATE(fecha) AS fecha_base
            FROM staging.ventas_staging
            UNION
            SELECT DATE(fecha_carga)
            FROM staging.inventario_staging
        ) f;
        """,

        # 📦 DIM_PRODUCTO (ahora incluye talla y color)
        """
        INSERT INTO warehouse.dim_producto (
            id_producto,
            producto,
            categoria,
            talla,
            color,
            precio_adquisicion
        )
        SELECT DISTINCT
            id_producto,
            producto,
            categoria,
            talla,
            color,
            precio_adquisicion
        FROM staging.inventario_staging;
        """,

        # 👤 DIM_CLIENTE
        """
        INSERT INTO warehouse.dim_cliente (
            id_cliente,
            nombre_cliente,
            ubicacion_cliente,
            genero,
            fecha_registro,
            canal_preferido
        )
        SELECT DISTINCT
            id_cliente,
            nombre_cliente,
            ubicacion_cliente,
            genero,
            fecha_registro,
            canal_preferido
        FROM staging.clientes_staging;
        """,

        # 💳 DIM_MEDIO_PAGO
        """
        INSERT INTO warehouse.dim_medio_pago (medio_pago)
        SELECT DISTINCT medio_pago
        FROM staging.ventas_staging;
        """
    ]

    with engine.begin() as conn:
        for query in queries:
            conn.execute(text(query))

    print("✔ Dimensiones cargadas correctamente\n")


# ==========================
# 🔹 CARGA FACT TABLES
# ==========================

def load_fact(engine):
    print("📈 Cargando fact tables...")

    query_ventas = """
    INSERT INTO warehouse.fact_ventas (
    id_venta,
    id_fecha,
    id_cliente,
    id_producto,
    id_medio_pago,
    cantidad,
    precio_venta_unitario,
    total_venta
    )
    SELECT
        v.id_venta,
        DATE(v.fecha),
        v.id_cliente,
        v.id_producto,
        mp.id_medio_pago,
        v.cantidad,
        i.precio_venta_unitario,
        v.cantidad * i.precio_venta_unitario
    FROM staging.ventas_staging v
    JOIN staging.inventario_staging i
        ON v.id_producto = i.id_producto
    JOIN warehouse.dim_medio_pago mp
        ON v.medio_pago = mp.medio_pago
    JOIN warehouse.dim_producto dp
        ON v.id_producto = dp.id_producto
    JOIN warehouse.dim_cliente dc
        ON v.id_cliente = dc.id_cliente;
    """

    query_inventario = """
        INSERT INTO warehouse.fact_inventario (
            id_producto,
            stock_actual
        )
        SELECT
            i.id_producto,
            i.stock_actual
        FROM staging.inventario_staging i;
    """

    with engine.begin() as conn:
        conn.execute(text(query_ventas))
        conn.execute(text(query_inventario))

    print("✔ Fact tables cargadas correctamente\n")


# ==========================
# 🔹 MAIN PIPELINE
# ==========================

def run_warehouse():
    engine = get_engine()

    print("🚀 Iniciando ETL staging ➜ WAREHOUSE\n")

    truncate_warehouse(engine)
    load_dimensions(engine)
    load_fact(engine)

    print("🎉 ETL completado exitosamente!")


if __name__ == "__main__":
    run_warehouse()