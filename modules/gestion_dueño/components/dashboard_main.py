import streamlit as st
import pandas as pd
# Importamos servicios desde el módulo de ingesta (compartidos)
from modules.ingesta_ventas.services.db_service import insert_sales_to_db, sql
from libs.logger import logInfo, logError

def render_owner_dashboard():
    """
    Dashboard Holístico para el Dueño: Visualización, Edición y Confirmación de Datos.
    """
    from modules.ingesta_ventas.services.state_manager import init_staging_state
    init_staging_state()
    
    st.title("👨‍💼 Panel de Control del Dueño")
    st.markdown("---")

    # --- PESTAÑAS DE REVISIÓN ---
    tab_ventas, tab_inventario, tab_clientes, tab_historial = st.tabs([
        "📥 Ventas Pendientes (Raw)", 
        "📦 Inventario Pendiente (Raw)",
        "👥 Clientes Nuevos (Raw)",
        "📊 Historial de BD"
    ])

    with tab_ventas:
        if st.session_state.staging_ventas.empty:
            st.info("No hay ventas pendientes de revisión en este momento.")
        else:
            st.warning("⚠️ Revisa y edita las celdas antes de guardar en la base de datos.")
            
            # Editor de Datos con validaciones implícitas
            edited_df = st.data_editor(
                st.session_state.staging_ventas,
                use_container_width=True,
                num_rows="dynamic",
                key="editor_ventas_staging",
                column_config={
                    "id_producto": st.column_config.NumberColumn("ID Prod", disabled=True),
                    "precio": st.column_config.NumberColumn("Precio", min_value=0.0, format="S/ %.2f"),
                    "cantidad": st.column_config.NumberColumn("Cant", min_value=1),
                    "medio_pago": st.column_config.SelectboxColumn("Pago", options=["Efectivo", "Yape", "Plin", "Tarjeta", "Transferencia"]),
                    "origen": st.column_config.TextColumn("Origen", disabled=True)
                }
            )

            # Botones de Acción
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                if st.button("🗑️ Vaciar Listado", use_container_width=True):
                    from modules.ingesta_ventas.services.state_manager import clear_staging
                    clear_staging("ventas")
                    st.rerun()
            
            with c2:
                if st.button("🔮 Auditar con IA", use_container_width=True):
                    from modules.ingesta_ventas.services.extraction_service import detect_business_antipatterns
                    import json
                    
                    # Convertimos el staging a JSON para que la IA lo analice
                    staging_json = edited_df.to_json(orient='records')
                    
                    with st.spinner("🤖 Gemini está auditando tus ventas..."):
                        audit_res = detect_business_antipatterns(staging_json)
                        warnings = audit_res.get("warnings", [])
                        
                        if not warnings:
                            st.success("✅ No se detectaron anomalías de negocio. ¡Todo se ve perfecto!")
                        else:
                            st.subheader("⚠️ Hallazgos de la Auditoría IA")
                            for w in warnings:
                                color = "red" if w["gravedad"] == "Alta" else ("orange" if w["gravedad"] == "Media" else "blue")
                                with st.expander(f":{color}[{w['gravedad']}] - {w['mensaje']}"):
                                    st.markdown(f"**Consecuencia:** {w['consecuencia']}")
                                    st.info("💡 Sugerencia: Revisa los precios o la cantidad para este registro.")

            with c3:
                if st.button("✅ Confirmar y Guardar todo", type="primary", use_container_width=True):
                    # Lógica de persistencia final
                    save_staging_ventas(edited_df)

    with tab_inventario:
        if st.session_state.staging_inventario.empty:
            st.info("No hay actualizaciones de inventario pendientes.")
        else:
            edited_inv = st.data_editor(st.session_state.staging_inventario, use_container_width=True, key="editor_inv_staging")
            if st.button("🚀 Confirmar Carga de Inventario", type="primary", use_container_width=True):
                from modules.ingesta_ventas.services.db_service import upsert_inventory_bulk
                res = upsert_inventory_bulk(edited_inv.to_dict('records'))
                if res["success"]:
                    st.success(res["message"])
                    from modules.ingesta_ventas.services.state_manager import clear_staging
                    clear_staging("inventario")
                    st.rerun()

    with tab_clientes:
        if st.session_state.staging_clientes.empty:
            st.info("No hay clientes pendientes de registro.")
        else:
            # En Clientes, solemos querer upsert o simplemente ignorar si ya existen
            edited_cli = st.data_editor(st.session_state.staging_clientes, use_container_width=True, key="editor_cli_staging")
            if st.button("💾 Registrar Clientes Seleccionados", type="primary", use_container_width=True):
                from modules.ingesta_ventas.services.db_service import insert_new_client
                success_count = 0
                for c in edited_cli.to_dict('records'):
                    res = insert_new_client(c)
                    if res["success"]: success_count += 1
                
                st.success(f"Se registraron {success_count} clientes.")
                from modules.ingesta_ventas.services.state_manager import clear_staging
                clear_staging("clientes")
                st.rerun()

    with tab_historial:
        st.markdown("### 🔍 Consultas Directas a la BD")
        # Referencia cruzada al componente de visualización
        from modules.ingesta_ventas.components.database_viewer import render_db_tab
        render_db_tab()

def save_staging_ventas(df):
    """
    Persiste el DataFrame editado en la base de datos real.
    """
    if df.empty:
        st.error("No hay datos para guardar.")
        return

    # Convertir DataFrame a lista de diccionarios para db_service
    sales_list = df.to_dict('records')
    
    # Preparar datos
    formatted_sales = []
    for s in sales_list:
        formatted_sales.append({
            "id_producto_directo": s.get("id_producto"),
            "producto": s.get("producto"),
            "talla": s.get("talla"),
            "color": s.get("color"),
            "cantidad": s.get("cantidad"),
            "precio": s.get("precio"),
            "nombre_cliente": s.get("cliente"),
            "medio_pago": s.get("medio_pago"),
            "fecha_registro": s.get("fecha_registro"),
            "categoria": s.get("categoria")
        })

    with st.spinner("Guardando en base de datos..."):
        res = insert_sales_to_db(formatted_sales)
        if res["success"]:
            st.success(res["message"])
            from modules.ingesta_ventas.services.state_manager import clear_staging
            clear_staging("ventas")
            st.balloons()
            st.rerun()
        else:
            st.error(res["message"])
