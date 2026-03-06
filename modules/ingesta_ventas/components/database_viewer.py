import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
import os
import math
from dotenv import load_dotenv

def render_db_tab():
    st.header("🗄️ Control de Base de Datos (CRUD)")
    st.caption("Gestiona de forma estructurada los registros transaccionales (Raw). Edita o avanza por páginas seguras.")

    load_dotenv()
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_schema = os.getenv("DB_SCHEMA", "raw")

    def get_conn():
        try:
            return psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_pass,
                host=db_host,
                port=db_port
            )
        except Exception as e:
            st.error(f"Error de Conexión: {e}")
            return None

    # TABS por tabla
    tab_ven, tab_inv, tab_cli = st.tabs(["🛒 Ventas", "📦 Inventario", "👥 Clientes"])
    
    tab_configs = [
        ("ventas_raw", "id_venta", tab_ven),
        ("inventario_raw", "id_producto", tab_inv),
        ("clientes_raw", "id_cliente", tab_cli)
    ]
    
    # Manejo Goblal de Conexión en Lectura/Pagina
    conn = get_conn()
    if not conn:
        return
        
    for table_name, pk_col, tab_ui in tab_configs:
        with tab_ui:
            # Control de Estado por Tab
            page_key = f"page_{table_name}"
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
                
            limit = 10
            
            with conn.cursor() as cur:
                # Contar totales
                query_count = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(sql.Identifier(db_schema), sql.Identifier(table_name))
                cur.execute(query_count)
                total_records = cur.fetchone()[0]
                total_pages = math.ceil(total_records / limit) if total_records > 0 else 1
                
            col_pag1, col_pag2, col_pag3 = st.columns([1,2,1])
            with col_pag1:
                if st.button("⬅️ Anterior", key=f"prev_{table_name}") and st.session_state[page_key] > 1:
                    st.session_state[page_key] -= 1
                    st.rerun()
            with col_pag2:
                st.markdown(f"<div style='text-align: center'>Página {st.session_state[page_key]} de {total_pages} (Total: {total_records})</div>", unsafe_allow_html=True)
            with col_pag3:
                if st.button("Siguiente ➡️", key=f"next_{table_name}") and st.session_state[page_key] < total_pages:
                    st.session_state[page_key] += 1
                    st.rerun()
                    
            offset = (st.session_state[page_key] - 1) * limit
            
            # Traer data de la página actual
            query_data = f"SELECT * FROM {db_schema}.{table_name} ORDER BY {pk_col} DESC LIMIT {limit} OFFSET {offset}"
            try:
                df = pd.read_sql_query(query_data, conn)
                
                # Renderizar Editor Interactivo
                st.write("⚠️ *Puedes modificar/borrar las celdas directamente. Guarda los cambios abajo.*")
                
                # Deshabilitar edición del PK
                col_cfg = {
                    pk_col: st.column_config.NumberColumn(disabled=True)
                }
                
                edited_df = st.data_editor(
                    df,
                    num_rows="dynamic",
                    width="stretch",
                    key=f"editor_{table_name}",
                    column_config=col_cfg
                )
                
                # Identificar cambios del state del editor
                editor_state = st.session_state[f"editor_{table_name}"]
                
                has_edits = bool(editor_state["edited_rows"] or editor_state["added_rows"] or editor_state["deleted_rows"])
                
                if has_edits:
                    if st.button("💾 Guardar Cambios en BD", type="primary", key=f"save_{table_name}"):
                        try:
                            # Creamos nueva conexión para escritura aislada
                            w_conn = get_conn()
                            with w_conn:
                                with w_conn.cursor() as cur:
                                    # 1. Aplicar Actualizaciones
                                    for row_idx, changes in editor_state["edited_rows"].items():
                                        pk_id = df.iloc[int(row_idx)][pk_col] # ID original antes del edit
                                        for col, new_val in changes.items():
                                            update_qry = sql.SQL("UPDATE {}.{} SET {} = %s WHERE {} = %s").format(
                                                sql.Identifier(db_schema), sql.Identifier(table_name),
                                                sql.Identifier(col), sql.Identifier(pk_col)
                                            )
                                            cur.execute(update_qry, (new_val, pk_id))
                                            
                                    # 2. Aplicar Eliminaciones (se indexa por el original)
                                    # Las filas se envían como ints
                                    for d_idx in sorted(editor_state["deleted_rows"], reverse=True):
                                        pk_id_del = df.iloc[int(d_idx)][pk_col]
                                        del_qry = sql.SQL("DELETE FROM {}.{} WHERE {} = %s").format(
                                            sql.Identifier(db_schema), sql.Identifier(table_name), sql.Identifier(pk_col)
                                        )
                                        cur.execute(del_qry, (pk_id_del,))
                                        
                                    # 3. Insertar Nuevos (agregados via dynamic rows UI)
                                    for new_row in editor_state["added_rows"]:
                                        cols = []
                                        vals = []
                                        for c, v in new_row.items():
                                            if c != pk_col and pd.notna(v) and v != "":
                                                cols.append(sql.Identifier(c))
                                                vals.append(v)
                                                
                                        if cols:
                                            insert_qry = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
                                                sql.Identifier(db_schema), sql.Identifier(table_name),
                                                sql.SQL(', ').join(cols),
                                                sql.SQL(', ').join(sql.Placeholder() * len(vals))
                                            )
                                            cur.execute(insert_qry, vals)
                                            
                            st.success("¡Base de datos actualizada con éxito!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al escribir en la Base de Datos: {e}")
                        finally:
                            if w_conn: w_conn.close()
            
            except Exception as e:
                st.error(f"Error al cargar tabla: {e}")

    if conn:
        conn.close()

