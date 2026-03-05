import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from scripts.orchestrator import run_etl_warehouse_pipeline
load_dotenv()


def get_engine():
    """Función auxiliar para centralizar la conexión."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")

def render_dashboard():

    # ⚙ CONFIGURACIÓN (SOLO UNA VEZ Y AL INICIO)
    st.set_page_config(page_title="Dashboard KPIs", layout="wide")

    # DATABASE_URL = os.getenv("DATABASE_URL")
    engine = get_engine()

    # 🎨 ESTILO GENERAL
    st.markdown("""
        <style>
            .main {
                /* Let Streamlit handle main background */
            }
            h1 {
                text-align: center;
                font-weight: 700;
                color: white;
            }
            .stMetric {
                background-color: #262730; /* Dark theme card background */
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
            }
            .stMetric label {
                color: #A0AAB2 !important; /* Lighter grey for metric label */
            }
            div[data-testid="stMetricValue"] {
                color: white !important; /* Force white for the number */
            }
            div[data-testid="stContainer"] {
                background-color: #262730;
                padding: 25px;
                border-radius: 14px;
                border: 1px solid #3d3d4e;
                box-shadow: 0px 6px 18px rgba(0,0,0,0.3);
                margin-bottom: 25px;
            }
            div[data-testid="stContainer"] h3 {
                color: #60B4FF !important; /* Light blue for container headers */
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>📊 Dashboard Ejecutivo de Datamark</h1>", unsafe_allow_html=True)
    
    
    # ================= CONTROL PIPELINE =================

    if "pipeline_running" not in st.session_state:
        st.session_state.pipeline_running = False

    col_btn1, col_btn2 = st.columns([1,4])

    with col_btn1:
        if st.button("🔄 Actualizar datos"):
            st.session_state.pipeline_running = True
            with st.spinner("Ejecutando pipeline..."):
                run_etl_warehouse_pipeline()
            st.success("Datos actualizados correctamente")
            st.session_state.pipeline_running = False

    with col_btn2:
        st.caption("Ejecuta el pipeline antes de analizar los datos")
    
    
    # ================= PRIMERA FILA =================

    query_fechas = """
    SELECT MIN(id_fecha) AS fecha_min,
           MAX(id_fecha) AS fecha_max
    FROM warehouse.fact_ventas;
    """

    df_fechas = pd.read_sql(query_fechas, engine)

    fecha_min = df_fechas["fecha_min"][0]
    fecha_max = df_fechas["fecha_max"][0]

    if pd.isna(fecha_min) or pd.isna(fecha_max):
        st.warning("⚠️ No hay datos de ventas en el Data Warehouse. Por favor, ve a la pestaña de Ingesta, sube algunas ventas, y luego pulsa 'Actualizar datos' aquí arriba.")
        st.stop()
        return

    fecha_seleccion = st.date_input(
        "📅 Selecciona rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )

    query_kpi = f"""
    SELECT 
        SUM(total_venta) AS ventas_totales,
        SUM(cantidad) AS unidades_vendidas,
        COUNT(DISTINCT id_cliente) AS clientes_unicos,
        SUM(total_venta) / COUNT(DISTINCT id_venta) AS ticket_promedio
    FROM warehouse.fact_ventas
    WHERE id_fecha BETWEEN '{fecha_seleccion[0]}' AND '{fecha_seleccion[1]}';
    """

    df = pd.read_sql(query_kpi, engine)

    ventas_totales = df["ventas_totales"][0]
    unidades_vendidas = df["unidades_vendidas"][0]
    clientes_unicos = df["clientes_unicos"][0]
    ticket_promedio = df["ticket_promedio"][0]

    st.markdown("""
    <h3 style='color:#60B4FF; border-left: 6px solid #60B4FF; padding-left:10px;'>
    📊 Análisis de Rendimiento
    </h3>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Ventas Totales", f"${ventas_totales:,.0f}")
    col2.metric("📦 Unidades Vendidas", f"{unidades_vendidas:,.0f}")
    col3.metric("👥 Clientes Únicos", f"{clientes_unicos:,.0f}")
    col4.metric("🧾 Ticket Promedio", f"${ticket_promedio:,.2f}")

    st.divider()

    # ================= SEGUNDA FILA =================
    st.markdown("""
    <h3 style='color:#1F4E79; border-left: 6px solid #1F4E79; padding-left:10px;'>
    📦 Análisis de Productos
    </h3>
    """, unsafe_allow_html=True)

       
    query_linea = f"""
    SELECT id_fecha,
           SUM(total_venta) AS ventas_diarias
    FROM warehouse.fact_ventas
    WHERE id_fecha BETWEEN '{fecha_seleccion[0]}' AND '{fecha_seleccion[1]}'
    GROUP BY id_fecha
    ORDER BY id_fecha;
    """

    df_linea = pd.read_sql(query_linea, engine)

    query_top = f"""
    SELECT p.producto,
           SUM(f.total_venta) AS ventas_totales
    FROM warehouse.fact_ventas f
    JOIN warehouse.dim_producto p 
        ON f.id_producto = p.id_producto
    WHERE f.id_fecha BETWEEN '{fecha_seleccion[0]}' AND '{fecha_seleccion[1]}'
    GROUP BY p.producto
    ORDER BY ventas_totales DESC
    LIMIT 10;
    """

    df_top = pd.read_sql(query_top, engine)

    query_bottom = f"""
    SELECT p.producto,
           SUM(f.total_venta) AS ventas_totales
    FROM warehouse.fact_ventas f
    JOIN warehouse.dim_producto p 
        ON f.id_producto = p.id_producto
    WHERE f.id_fecha BETWEEN '{fecha_seleccion[0]}' AND '{fecha_seleccion[1]}'
    GROUP BY p.producto
    ORDER BY ventas_totales ASC
    LIMIT 10;
    """

    df_bottom = pd.read_sql(query_bottom, engine)

    colA, colB, colC = st.columns(3)

    with colA:
        with st.container(border=True):
            st.subheader("📈 Ventas por Fecha")
            fig_linea = px.line(df_linea, x="id_fecha", y="ventas_diarias", markers=True)
            fig_linea.update_layout(height=450, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_linea, use_container_width=True, key="fig_linea")

    with colB:
        with st.container(border=True):
            st.subheader("🔥 Top 10 Productos")
            fig_top = px.bar(df_top, x="ventas_totales", y="producto", orientation="h")
            fig_top.update_layout(height=450, yaxis=dict(categoryorder="total ascending"), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_top, use_container_width=True, key="fig_top")

    with colC:
        with st.container(border=True):
            st.subheader("📉 Productos Menos Vendidos")
            fig_bottom = px.bar(df_bottom, x="ventas_totales", y="producto", orientation="h")
            fig_bottom.update_layout(height=450, yaxis=dict(categoryorder="total ascending"), template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bottom, use_container_width=True, key="fig_bottom")

    st.divider()

    # ================= TERCERA FILA =================
    st.markdown("""
    <h3 style='color:#1F4E79; border-left: 6px solid #1F4E79; padding-left:10px;'>
    💰 Análisis de Ventas
    </h3>
    """, unsafe_allow_html=True)
    query_categoria = f"""
    SELECT p.categoria,
           SUM(f.total_venta) AS ventas_totales
    FROM warehouse.fact_ventas f
    JOIN warehouse.dim_producto p 
        ON f.id_producto = p.id_producto
    WHERE f.id_fecha BETWEEN '{fecha_seleccion[0]}' AND '{fecha_seleccion[1]}'
    GROUP BY p.categoria
    ORDER BY ventas_totales DESC;
    """

    df_categoria = pd.read_sql(query_categoria, engine)

    query_talla = f"""
    SELECT p.talla,
           SUM(f.total_venta) AS ventas_totales
    FROM warehouse.fact_ventas f
    JOIN warehouse.dim_producto p 
        ON f.id_producto = p.id_producto
    WHERE f.id_fecha BETWEEN '{fecha_seleccion[0]}' AND '{fecha_seleccion[1]}'
    GROUP BY p.talla
    ORDER BY ventas_totales DESC;
    """

    df_talla = pd.read_sql(query_talla, engine)

    query_color = f"""
    SELECT p.color,
           SUM(f.total_venta) AS ventas_totales
    FROM warehouse.fact_ventas f
    JOIN warehouse.dim_producto p 
        ON f.id_producto = p.id_producto
    WHERE f.id_fecha BETWEEN '{fecha_seleccion[0]}' AND '{fecha_seleccion[1]}'
    GROUP BY p.color
    ORDER BY ventas_totales DESC;
    """

    df_color = pd.read_sql(query_color, engine)

    fig_categoria = px.pie(df_categoria, names="categoria", values="ventas_totales")
    fig_talla = px.bar(df_talla, x="talla", y="ventas_totales")
    fig_color = px.pie(df_color, names="color", values="ventas_totales", hole=0.5)

    colX, colY, colZ = st.columns(3)

    with colX:
        with st.container(border=True):
            st.subheader("🥧 Ventas Totales por Categoría")
            fig_categoria.update_layout(height=450, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_categoria, use_container_width=True, key="fig_categoria")

    with colY:
        with st.container(border=True):
            st.subheader("📊 Ventas por Talla")
            fig_talla.update_layout(height=450, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_talla, use_container_width=True, key="fig_talla")

    with colZ:
        with st.container(border=True):
            st.subheader("🍩 Ventas por Color")
            fig_color.update_layout(height=450, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_color, use_container_width=True, key="fig_color")

    st.divider()
    st.write("Datos en tiempo real desde la base de datos 🚀")