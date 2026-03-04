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
        "📥 Solo ventas (Raw)", 
        "📦 Solo inventario (Raw)",
        "👥 Solo clientes (Raw)",
        "📊 Historial de BD"
    ])

    with tab_ventas:
        if st.session_state.staging_ventas.empty:
            st.info("No hay ventas en el consolidado en este momento.")
        else:
            st.info("📋 Vista consolidada de ventas (IDs visibles - No editables).")
            
            # Visor de Datos (Solo lectura)
            # Mostramos id_producto y advertencias para transparencia con el dueño
            st.dataframe(
                st.session_state.staging_ventas,
                width="stretch",
                hide_index=True,
                column_config={
                    "id_producto": st.column_config.NumberColumn("ID Resuelto", help="ID detectado automáticamente"),
                    "_warning": st.column_config.TextColumn("⚠️ Aviso", help="Advertencia sobre el producto o variante"),
                    "producto": st.column_config.TextColumn("Producto", disabled=True),
                    "precio": st.column_config.NumberColumn("Precio", format="S/ %.2f", disabled=True),
                    "cantidad": st.column_config.NumberColumn("Cant", disabled=True),
                    "medio_pago": st.column_config.TextColumn("Pago", disabled=True),
                    "origen": st.column_config.TextColumn("Origen", disabled=True)
                }
            )
            edited_df = st.session_state.staging_ventas

            # Botones de Acción
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                if st.button("🗑️ Vaciar Listado", width="stretch"):
                    from modules.ingesta_ventas.services.state_manager import clear_staging
                    clear_staging("ventas")
                    st.rerun()
            
            with c2:
                if st.button("🔮 Auditar con IA", width="stretch"):
                    from modules.ingesta_ventas.services.extraction_service import detect_business_antipatterns
                    import json
                    
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
                if st.button("✅ Confirmar y Guardar todo", type="primary", width="stretch"):
                    save_staging_ventas(edited_df)

    with tab_inventario:
        if st.session_state.staging_inventario.empty:
            st.info("No hay actualizaciones de inventario pendientes.")
        else:
            edited_inv = st.data_editor(st.session_state.staging_inventario, width="stretch", key="editor_inv_staging")
            if st.button("🚀 Confirmar Carga de Inventario", type="primary", width="stretch"):
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
            edited_cli = st.data_editor(st.session_state.staging_clientes, width="stretch", key="editor_cli_staging")
            if st.button("💾 Registrar Clientes Seleccionados", type="primary", width="stretch"):
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
        from modules.ingesta_ventas.components.database_viewer import render_db_tab
        render_db_tab()

def save_staging_ventas(df):
    """
    Persiste el DataFrame editado. Maneja fallos parciales manteniendo items en staging.
    """
    if df.empty:
        st.error("No hay datos para guardar.")
        return

    sales_list = df.to_dict('records')
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

    with st.spinner("Guardando en base de datos con validación estricta..."):
        res = insert_sales_to_db(formatted_sales)
        if res["success"]:
            st.success(res["message"])
            from modules.ingesta_ventas.services.state_manager import clear_staging
            clear_staging("ventas")
            st.balloons()
            st.rerun()
        else:
            st.error(res["message"])
            
            # Si hay fallos específicos, los informamos y no vaciamos el staging
            if "failed_items" in res:
                st.subheader("❌ Errores Críticos (No se guardó nada)")
                for item in res["failed_items"]:
                    st.warning(f"Fila {item['index'] + 1}: **{item['producto']}** - {item['razon']}")
                
                st.info("💡 Por favor corrige estos items en el origen o el inventario antes de reintentar.")
            else:
                st.error("Ocurrió un error inesperado al guardar.")
