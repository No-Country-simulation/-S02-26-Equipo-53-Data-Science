import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql

def render_db_tab():

    st.header("🔌 Conexión a PostgreSQL")

    # --- Configuración de Conexión ---
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # Obtener credenciales
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "")
    db_schema = os.getenv("DB_SCHEMA", "public")

    # Mostrar credenciales (Ocultar password)
    with st.expander("Configuración de Conexión"):
        st.write(f"Host: {db_host}, DB: {db_name}, User: {db_user}, Schema: {db_schema}")

    # Construir URI de conexión
    try:
        from urllib.parse import quote_plus
        encoded_pass = quote_plus(db_pass)
        conn_uri = f"postgresql://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}"
    except Exception:
        conn_uri = ""

    st.subheader("🔍 Estructura de Tablas")

    if st.button("Listar Tablas y Columnas"):
        try:
            with psycopg2.connect(conn_uri) as conn:
                with conn.cursor() as cursor:
                    # 1. Listar Tablas
                    query_tables = """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = %s
                    """
                    cursor.execute(query_tables, (db_schema,))
                    tables = cursor.fetchall()

                    if not tables:
                        st.warning(f"No se encontraron tablas en el esquema '{db_schema}'.")
                    
                    for table in tables:
                        table_name = table[0]
                        st.markdown(f"#### 📄 Tabla: `{table_name}`")
                        
                        # 2. Listar Columnas
                        query_columns = """
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns 
                            WHERE table_schema = %s AND table_name = %s
                            ORDER BY ordinal_position
                        """
                        cursor.execute(query_columns, (db_schema, table_name))
                        columns = cursor.fetchall()
                        
                        # Mostrar como dataframe
                        df_cols = pd.DataFrame(columns, columns=["Columna", "Tipo", "Nullable"])
                        st.dataframe(df_cols, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error al listar tablas: {e}")

    st.subheader("📝 Consulta SQL Manual")
    
    default_query = f"SELECT * FROM {db_schema}.ventas_raw LIMIT 10" if db_schema else "SELECT 1"
    query = st.text_area("SQL:", value=default_query, height=100)
    
    if st.button("🚀 Ejecutar SQL", type="primary"):
        if not query.strip():
            st.warning("La consulta no puede estar vacía.")
            return

        try:
            with st.spinner("Ejecutando consulta..."):
                with psycopg2.connect(conn_uri) as conn:
                    df = pd.read_sql_query(query, conn)
                    st.success(f"Consulta ejecutada exitosamente. Filas retornadas: {len(df)}")
                    st.dataframe(df, use_container_width=True)

        except psycopg2.OperationalError as e:
            st.error(f"❌ Error de Conexión: No se pudo conectar a la base de datos.\n\nDetalle: {e}")
        except psycopg2.Error as e:
            st.error(f"❌ Error de Base de Datos:\n{e}")
        except Exception as e:
            st.error(f"❌ Error Inesperado:\n{e}")
