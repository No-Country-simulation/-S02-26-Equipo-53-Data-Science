import streamlit as st
import sys
import os

import sys
import os

# Agregamos la carpeta libs local al path para cargar dependencias instaladas localmente
# Esto es necesario porque el entorno global de Python 3.14 en C: no tiene espacio
libs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'libs')
sys.path.insert(0, libs_path) # Insertar al principio para prioridad
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print(f"DEBUG: sys.path includes: {libs_path}")
print(f"DEBUG: libs exists? {os.path.exists(libs_path)}")

from libs.logger import logInfo, logSequence, logError
from .components.voice_input import voice_input_component
from .components.database_viewer import render_db_tab


if __name__ == "__main__":
    st.set_page_config(
        page_title="Hola Mundo Streamlit",
        page_icon="👋",
        layout="centered"
    )

def main():
    logSequence("Iniciando aplicación", "Hola Mundo")

    st.title("Carga de datos")
    st.write("Selecciona el método de ingreso de ventas:")
    
    # --- Navegación Principal ---
    tab1, tab2, tab3, tab4 = st.tabs(["🎙️ Dictado IA", "👆 Entrada Manual", "📂 Carga Masiva", "🔍 Consulta BD"])
    
    with tab1:
        st.header("Entrada libre por voz y texto")
        render_voice_agent_tab()
    
    with tab2:
        from .components.manual_input import render_manual_input_tab
        render_manual_input_tab()
        
    with tab3:
        from .components.mass_upload import render_mass_upload_tab
        render_mass_upload_tab()

    with tab4:
        render_db_tab()
        
def render_voice_agent_tab():
    # --- Inicialización de Estado ---
    if 'sales_data' not in st.session_state:
        st.session_state.sales_data = []

    # --- Lógica de Sincronización (CRÍTICO para evitar StreamlitAPIException) ---
    # Si hay texto pendiente de la voz (capturado al final del run anterior), 
    # lo añadimos ahora ANTES de que el text_area se instancia.
    if 'pending_voice_text' in st.session_state and st.session_state.pending_voice_text:
        current_val = st.session_state.get('text_area_input', "")
        new_val = (current_val + "\n" + st.session_state.pending_voice_text).strip()
        st.session_state.text_area_input = new_val
        st.session_state.pending_voice_text = None # Limpiar

    # Área de texto editable (vinculada al estado)
    st.text_area(
        "Detalle de ventas (dictado acumulado):", 
        height=200,
        key="text_area_input",
        placeholder="Aquí aparecerá lo que grabes. Puedes editarlo o escribir manualmente..."
    )

    # --- Controles (Grabar y Procesar) ---
    col_voice, col_process = st.columns([0.2, 0.8], vertical_alignment="center")

    with col_voice:
        # Ajuste fino de alineación vertical
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True) 
        # Botón de Grabación
        voice_fragment = voice_input_component(key="voice_btn_tab")
        
        if voice_fragment:
            # Guardamos para el siguiente run
            st.session_state.pending_voice_text = voice_fragment
            st.rerun()

    with col_process:
        # Botón de Procesamiento
        if st.button("⚡ Procesar Ventas", type="primary", use_container_width=True):
            input_text = st.session_state.get('text_area_input', "")
            if not input_text.strip():
                st.warning("⚠️ No hay texto para procesar. Graba o escribe algo primero.")
            else:
                with st.spinner("Analizando múltiples ventas con IA (Gemini 2.5)..."):
                    from .services.extraction_service import extract_sales_data
                    from .services.db_service import search_inventory_fuzzy
                    result = extract_sales_data(input_text)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        processed_sales = []
                        for item in result["data"]:
                            dictated = item.get("producto_dictado", "")
                            
                            # Intentar resolver usando DB
                            matches = search_inventory_fuzzy(dictated, limit=5)
                            
                            base_sale = {
                                "producto_dictado": dictated,
                                "cantidad": item.get("cantidad", 1),
                                "nombre_cliente": item.get("nombre_cliente", "Anónimo"),
                                "ubicacion_cliente": item.get("ubicacion_cliente", "Desconocido"),
                                "genero": item.get("genero", "U"),
                                "medio_pago": item.get("medio_pago", "Efectivo"),
                                "fecha_registro": item.get("fecha_registro"),
                                "visto_bueno": False
                            }
                            
                            if not matches:
                                # No hay coincidencias en BD -> Conflicto
                                base_sale["estado_match"] = "No Encontrado"
                                base_sale["id_producto"] = None
                                base_sale["producto_oficial"] = None
                                base_sale["talla"] = None
                                base_sale["color"] = None
                                base_sale["precio"] = 0.0
                                base_sale["opciones_variante"] = []
                            elif len(matches) == 1 and len(matches[0]["variantes"]) == 1:
                                # Match exacto y Variante Única -> Perfecto
                                variante = matches[0]["variantes"][0]
                                base_sale["estado_match"] = "Exacto"
                                base_sale["id_producto"] = variante["id_producto"]
                                base_sale["producto_oficial"] = matches[0]["producto_oficial"]
                                base_sale["talla"] = variante["talla"]
                                base_sale["color"] = variante["color"]
                                base_sale["precio"] = variante["precio"]
                                base_sale["opciones_variante"] = []
                            else:
                                # Existen variantes, hay que aplanar opciones para el selectbox
                                opciones = []
                                for m in matches:
                                    for v in m["variantes"]:
                                        # String visual para el selectbox
                                        label = f"{m['producto_oficial']} | {v['talla']} | {v['color']} | S/{v['precio']} (ID:{v['id_producto']})"
                                        opciones.append(label)
                                        
                                base_sale["estado_match"] = "Ambigüedad"
                                base_sale["id_producto"] = None # Requiere acción manual
                                base_sale["producto_oficial"] = "-- Elige Variante --"
                                base_sale["talla"] = None
                                base_sale["color"] = None
                                base_sale["precio"] = 0.0
                                base_sale["opciones_variante"] = opciones # Inyectamos lista de strings
                                
                            processed_sales.append(base_sale)
                            
                        st.session_state.sales_data = processed_sales
                        st.session_state.last_execution_time = result["duration"]
                        st.rerun()

    # --- Vista de Tabla de Resultados ---
    if st.session_state.sales_data:
        st.divider()
        
        # Métrica de tiempo
        if 'last_execution_time' in st.session_state:
            st.caption(f"⚡ Procesado por Gemini 2.5 Flash en **{st.session_state.last_execution_time:.2f} segundos**")
        
        st.markdown("### 📋 Tabla de Ventas (Editable)")
        
        # Pre-procesamiento: asegurar que fecha_registro sea datetime.date para el editor
        import datetime
        for row in st.session_state.sales_data:
            if isinstance(row.get('fecha_registro'), str):
                try:
                    row['fecha_registro'] = datetime.datetime.strptime(row['fecha_registro'], "%Y-%m-%d").date()
                except ValueError:
                    pass # Dejar como string si falla el parseo
        
        # --- Indicador de Campos Vacíos y Visto Bueno ---
        import base64
        
        # Icono ⚠️ (Pendiente)
        warning_svg = """
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="10" cy="10" r="9" fill="#362d00" stroke="#facc15" stroke-width="1.5"/>
          <text x="10" y="14.5" fill="#facc15" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle">!</text>
        </svg>
        """
        # Icono ✅ (OK/Aprobado)
        ok_svg = """
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="10" cy="10" r="9" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
          <path d="M6 10L9 13L14 7" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """
        
        def get_icon_url(svg_str):
            b64 = base64.b64encode(svg_str.encode()).decode()
            return f"data:image/svg+xml;base64,{b64}"

        warning_url = get_icon_url(warning_svg)
        ok_url = get_icon_url(ok_svg)

        def check_row_status(row):
            # Check for conflict resolution requirement:
            if row.get("estado_match") == "Ambigüedad" or row.get("producto_oficial") == "-- Elige Variante --":
                return warning_url
                
            # Resto de validaciones estándar
            missing = False
            for k, v in row.items():
                if k in ["estado", "visto_bueno", "opciones_variante", "id_producto"]: continue
                if v is None or v == "" or v == "Desconocido" or v == "Anónimo":
                    missing = True
                    break
            
            # Si tiene visto bueno explícito o si está Exacto
            if (not missing and row.get("estado_match") == "Exacto") or row.get("visto_bueno", False):
                return ok_url
            return warning_url

        # Para cada fila, asegurar que si es ambigüedad, mostramos el String visual
        display_data = []
        for row in st.session_state.sales_data:
            new_row = row.copy()
            if "visto_bueno" not in new_row:
                new_row["visto_bueno"] = False
            new_row["estado"] = check_row_status(new_row)
            display_data.append(new_row)

        column_order = [
            "estado", "visto_bueno", "producto_dictado", "producto_oficial", "talla", "color", "precio", "cantidad", 
            "nombre_cliente", "ubicacion_cliente", "genero", 
            "medio_pago", "fecha_registro"
        ]
        
        column_config = {
            "estado": st.column_config.ImageColumn("Stat", width="small", help="Estado de validación"),
            "visto_bueno": st.column_config.CheckboxColumn("V.B.", help="Forzar aprobación manual de IA"),
            "producto_dictado": st.column_config.TextColumn("Voz Extraida", disabled=True),
            "talla": st.column_config.TextColumn("Talla", disabled=True),
            "color": st.column_config.TextColumn("Color", disabled=True),
            "precio": st.column_config.NumberColumn("Precio Final Unit.", disabled=True, format="S/ %.2f"),
            "cantidad": st.column_config.NumberColumn("Cant.", min_value=1, step=1),
            "nombre_cliente": st.column_config.TextColumn("Cliente"),
            "ubicacion_cliente": st.column_config.TextColumn("Ubicación"),
            "genero": st.column_config.SelectboxColumn("Género", options=["M", "F", "U"]),
            "medio_pago": st.column_config.SelectboxColumn("Medio Pago", options=["Efectivo", "Yape", "Plin", "Tarjeta", "Transferencia", "Otros"]),
            "fecha_registro": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
        }
        
        # Inyectar selectbox dinámico por fila si hay conflicto
        # Streamlit Data Editor no soporta opciones dinámicas por fila limpiamente en column_config,
        # así que creamos una lista maestra con TODAS las opciones posibles de esas filas para el Selector
        todas_las_opciones = ["-- Elige Variante --"]
        for row in display_data:
             opciones = row.get("opciones_variante", [])
             if isinstance(opciones, list):
                 for b in opciones:
                      if b not in todas_las_opciones:
                           todas_las_opciones.append(b)
                           
        column_config["producto_oficial"] = st.column_config.SelectboxColumn(
             "ID BD (Match)", 
             options=todas_las_opciones,
             required=True
        )

        edited_df = st.data_editor(
            display_data,
            num_rows="dynamic",
            use_container_width=True,
            key="sales_editor",
            column_order=column_order,
            column_config=column_config,
            hide_index=True
        )
        
        # Sincronizador reverso: Si el usuario eligió una variante del dropdown, parsearla y extraer ID
        import re
        for i, edited_row in enumerate(edited_df):
             # Si se alteró el selectbox
             if edited_row.get("estado_match") == "Ambigüedad" and edited_row.get("producto_oficial") != "-- Elige Variante --":
                  raw_str = edited_row["producto_oficial"]
                  # Extract ID using RegEx: (ID: 15)
                  match_id = re.search(r"\(ID:(\d+)\)", raw_str)
                  if match_id:
                       id_real = int(match_id.group(1))
                       # Como sabemos la id real, podemos considerarlo resuelto
                       edited_row["id_producto"] = id_real
                       edited_row["estado_match"] = "Exacto manual"
                       # Optional: Parsear talla color para reflejo (asumiremos que db_service hará el insert con ID)
                       
             # Guardamos cambio
             st.session_state.sales_data[i] = edited_row
        
        # Sincronizar cambios del editor con el estado de la sesión
        # Importante: Solo actualizamos si hay cambios reales para evitar bucles de rerun innecesarios
        st.session_state.sales_data = edited_df

        col_actions = st.columns([0.2, 0.8])
        with col_actions[0]:
            # Verificar si todos tienen check verde (ok_url)
            can_save = all(check_row_status(row) == ok_url for row in st.session_state.sales_data)
            

            if st.button("💾 Guardar Todo", disabled=not can_save, help="Solo habilitado si todas las filas están OK o tienen V.B."):
                st.toast(f"Guardando {len(edited_df)} registros en BD...", icon="⏳")
                
                # Integración con Servicio de Base de Datos
                from .services.db_service import insert_sales_to_db
                
                # Convertir dataframe a lista de dicts limpios mapeando ID correcto
                if isinstance(edited_df, list):
                    temp_list = edited_df
                else:
                    try:
                        temp_list = edited_df.to_dict('records')
                    except AttributeError:
                         temp_list = edited_df

                sales_list = []
                for t in temp_list:
                     sales_list.append({
                         "producto": None, # Force reliance on ID below
                         "id_producto_directo": t.get("id_producto"), # New internal bridge field
                         "talla": None, 
                         "color": None,
                         "cantidad": t.get("cantidad", 1),
                         "medio_pago": t.get("medio_pago", "Efectivo"),
                         "nombre_cliente": t.get("nombre_cliente", "Anónimo"),
                         "fecha_registro": t.get("fecha_registro")
                     })

                result = insert_sales_to_db(sales_list)
                
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    logInfo(f"Guardado exitoso en BD: {len(sales_list)} registros.")
                    # Limpiar estado
                    st.session_state.sales_data = []
                    st.session_state.raw_voice_text = ""
                    import time
                    time.sleep(2) # Dar tiempo a leer el mensaje
                    st.rerun()
                else:
                    msg = result['message']
                    if "permission denied" in msg:
                        st.error("⛔ **ERROR DE PERMISOS EN BASE DE DATOS**")
                        st.markdown("""
                        El usuario de base de datos **no tiene permiso** para escribir en la tabla.
                        
                        **Solución:**
                        Pide al administrador de la BD que ejecute esto:
                        ```sql
                        GRANT INSERT ON TABLE raw.ventas_raw TO "Oscar";
                        GRANT USAGE, SELECT ON SEQUENCE raw.ventas_raw_id_venta_seq TO "Oscar";
                        ```
                        """)
                    else:
                        st.error(f"❌ Error al guardar: {msg}")
                    logError(f"Fallo al guardar en BD: {msg}")
            
            if not can_save:
                st.caption("⚠️ Subsanar campos vacíos o dar Visto Bueno para guardar.")

if __name__ == "__main__":
    main()
