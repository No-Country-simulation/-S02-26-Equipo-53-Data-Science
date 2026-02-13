import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql

def render_db_tab():
    st.header("🔌 Conexión a PostgreSQL")

    # --- Configuración de Conexión ---
    # --- Configuración de Conexión ---
    import os
    from dotenv import load_dotenv
    load_dotenv()

    with st.expander("Configuración de Conexión", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            db_host = st.text_input("Host", value=os.getenv("DB_HOST", "localhost"), key="db_host")
            db_port = st.text_input("Port", value=os.getenv("DB_PORT", "5432"), key="db_port")
            db_name = st.text_input("Database", value=os.getenv("DB_NAME", "postgres"), key="db_name")
        with col2:
            db_user = st.text_input("User", value=os.getenv("DB_USER", "postgres"), key="db_user")
            db_pass = st.text_input("Password", value=os.getenv("DB_PASS", ""), type="password", key="db_pass")
            db_schema = st.text_input("Schema", value=os.getenv("DB_SCHEMA", "public"), key="db_schema")

    # Construir URI de conexión
    try:
        # Codificar contraseña para caracteres especiales si es necesario
        from urllib.parse import quote_plus
        encoded_pass = quote_plus(db_pass)
        conn_uri = f"postgresql://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}"
    except Exception:
        conn_uri = ""

    st.subheader("📝 Consulta SQL")
    
    default_query = f"SELECT * FROM {db_schema}.inventario_raw LIMIT 50" if db_schema else "SELECT 1"
    query = st.text_area("Escribe tu consulta aquí:", value=default_query, height=150)
    
    if st.button("🚀 Ejecutar Consulta", type="primary"):
        if not query.strip():
            st.warning("La consulta no puede estar vacía.")
            return

        try:
            with st.spinner("Ejecutando consulta..."):
                # Conexión efímera para esta consulta (Patrón simple para esta herramienta)
                # En una app real de alto tráfico, usaríamos un ConnectionPool global
                with psycopg2.connect(conn_uri) as conn:
                    
                    # Usar Pandas para leer SQL directamente es muy cómodo para reportes
                    df = pd.read_sql_query(query, conn)
                    
                    st.success(f"Consulta ejecutada exitosamente. Filas retornadas: {len(df)}")
                    st.dataframe(df, use_container_width=True)

        except psycopg2.OperationalError as e:
            st.error(f"❌ Error de Conexión: No se pudo conectar a la base de datos.\n\nDetalle: {e}")
        except psycopg2.Error as e:
            st.error(f"❌ Error de Base de Datos:\n{e}")
        except Exception as e:
            st.error(f"❌ Error Inesperado:\n{e}")
