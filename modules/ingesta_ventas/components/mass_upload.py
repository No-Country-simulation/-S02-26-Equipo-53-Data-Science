import streamlit as st
import pandas as pd
import io
from ..services.extraction_service import suggest_column_mapping, extract_product_attributes_batch
from ..services.db_service import upsert_inventory_bulk, resolve_and_insert_sales_bulk
from libs.logger import logError, logInfo

# Definir la estructura obligatoria que requiere la base de datos
TEMPLATE_INVENTARIO = ["producto", "categoria", "talla", "color", "stock_actual", "precio_adquisicion", "precio_venta"]
TEMPLATE_VENTAS = ["producto", "cantidad", "precio", "nombre_cliente", "medio_pago", "fecha_registro"]

def download_template_btn(tipo: str):
    """Genera un botón funcional para descargar un CSV de plantilla salvavidas."""
    cols = TEMPLATE_INVENTARIO if tipo == "Inventario" else TEMPLATE_VENTAS
    df_template = pd.DataFrame(columns=cols)
    buffer = io.BytesIO()
    df_template.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    
    st.download_button(
        label=f"⬇️ Descargar Plantilla '{tipo}' (Recomendado)",
        data=buffer,
        file_name=f"plantilla_{tipo.lower()}_datamark.csv",
        mime="text/csv",
        type="secondary",
        use_container_width=True
    )

def highlight_invalid_cells(val):
    """Pandas Styler: Pinta de rojo si un valor esperado estricto está vacío o es inválido"""
    if pd.isna(val) or val == "" or str(val).strip() == "":
         return 'background-color: #ffcccc; color: #900000;'
    return ''

def render_paso1_seleccion():
    st.subheader("Paso 1: ¿Qué deseas cargar?")
    col_inv, col_ven = st.columns(2)
    
    with col_inv:
        with st.container(border=True):
            st.markdown("### 📦 Inventario Inicial")
            st.caption("Carga tus productos, stock y precios base.")
            download_template_btn("Inventario")
            if st.button("Subir archivo de Inventario", key="btn_sel_inv", use_container_width=True):
                st.session_state.mass_upload_tipo = "Inventario"
                st.session_state.mass_upload_step = 2
                st.rerun()
                
    with col_ven:
        with st.container(border=True):
            st.markdown("### 📈 Historial de Ventas")
            st.caption("Sube tus ventas pasadas desde Excel.")
            download_template_btn("Ventas")
            if st.button("Subir archivo de Ventas", key="btn_sel_ven", use_container_width=True):
                 st.session_state.mass_upload_tipo = "Ventas"
                 st.session_state.mass_upload_step = 2
                 st.rerun()

def render_paso2_mapeador():
    tipo = st.session_state.mass_upload_tipo
    st.subheader(f"Paso 2: Subir y Mapear ({tipo})")
    
    if st.button("⬅️ Volver a Paso 1", key="btn_back_1"):
        st.session_state.mass_upload_step = 1
        st.session_state.mass_upload_file = None
        st.session_state.mass_upload_df = None
        st.session_state.mass_upload_mapping = {}
        st.rerun()
        
    archivo = st.file_uploader(f"Sube tu archivo de {tipo} (.csv, .xlsx)", type=["csv", "xlsx"])
    
    if archivo:
        try:
            if archivo.name.endswith(".csv"):
                 df_raw = pd.read_csv(archivo)
            else:
                 df_raw = pd.read_excel(archivo)
                 
            st.session_state.mass_upload_file = df_raw
            # Detectar si el usuario subió nuestra plantilla perfecta
            expected_cols = TEMPLATE_INVENTARIO if tipo == "Inventario" else TEMPLATE_VENTAS
            raw_cols = df_raw.columns.tolist()
            
            es_plantilla_perfecta = all(col in raw_cols for col in expected_cols)
            
            if es_plantilla_perfecta:
                st.success("✅ ¡Has subido la plantilla perfecta DATAMARK! Saltando al Paso 3...")
                # Auto mapear directo
                st.session_state.mass_upload_mapping = {c: c for c in expected_cols}
                st.session_state.mass_upload_step = 3
                import time
                time.sleep(1.5)
                st.rerun()
                return

            # Si es desordenado, correr el Mapper Inteligente (+ Gemini)
            st.info("💡 Hemos detectado un formato libre. Estamos analizando las columnas con IA para sugerirte emparejamientos...")
            
            # Cache del prompt gemini en session state para no repetirlo cada re-render de streamlit
            if 'gemini_suggestions' not in st.session_state:
                with st.spinner("🤖 Gemini está analizando tu Excel..."):
                     st.session_state.gemini_suggestions = suggest_column_mapping(raw_cols, expected_cols)
                     
            sug_map = st.session_state.gemini_suggestions.get("mapping", {})
            
            st.markdown("### Enlaza las columnas obligatorias")
            st.caption("Revisa que los datos de tu Excel correspondan a lo que DATAMARK necesita.")
            
            current_mapping = {}
            opciones_select = ["-- Faltante / Asignar Nulo --"] + raw_cols
            
            with st.form("form_mapeo"):
                for req_col in expected_cols:
                    # Sugerencia IA por defecto?
                    default_idx = 0
                    if req_col in sug_map:
                         try:
                             default_idx = opciones_select.index(sug_map[req_col])
                         except ValueError:
                             pass 
                             
                    val_seleccionado = st.selectbox(
                        f"Tu columna en Excel para 👉 **'{req_col}'**", 
                        options=opciones_select, 
                        index=default_idx
                    )
                    current_mapping[req_col] = val_seleccionado
                    
                enviar_mapeo = st.form_submit_button("Siguiente: Limpiar y Validar", type="primary")
            
            if enviar_mapeo:
                # Restricción: No puede haber obligatorios críticos nulos
                # (Para inventario, prod obliga. Para ventas: prod y precio obligan)
                errores = []
                if current_mapping.get("producto") == "-- Faltante / Asignar Nulo --":
                    errores.append("No puedes dejar el 'producto' faltante.")
                if tipo == "Ventas" and current_mapping.get("precio") == "-- Faltante / Asignar Nulo --":
                    errores.append("No puedes dejar el 'precio' faltante en las ventas.")

                if len(errores) > 0:
                    for e in errores: st.error(e)
                else:
                    st.session_state.mass_upload_mapping = current_mapping
                    st.session_state.mass_upload_step = 3
                    st.rerun()

        except Exception as e:
            st.error(f"No se pudo leer el archivo: {e}")

def render_paso3_validacion():
    tipo = st.session_state.mass_upload_tipo
    st.subheader(f"Paso 3: Extraer y Validar ({tipo})")
    
    col_b, _ = st.columns([2, 5])
    with col_b:
        if st.button("⬅️ Retrospecto al Mapeo", key="btn_back_2"):
            st.session_state.mass_upload_step = 2
            st.rerun()

    df_raw = st.session_state.mass_upload_file
    mapping = st.session_state.mass_upload_mapping
    
    # 1. Transformación inicial de Pandas basándose en Mapping
    df_clean = pd.DataFrame()
    for req_col, excel_col in mapping.items():
         if excel_col == "-- Faltante / Asignar Nulo --":
             df_clean[req_col] = None
         else:
             df_clean[req_col] = df_raw[excel_col]

    # Prevenir reprocesamiento IA guardando en session state
    if 'cleaned_dataframe' not in st.session_state:
        # APLICAR EXTRACCIÓN HÍBRIDA (IA + PANDAS)
        with st.spinner("🤖 Aplicando algoritmos híbridos de limpieza y extracción de atributos..."):
            
            # --- Tareas de Limpieza de Pandas ---
            if 'precio' in df_clean.columns:
                df_clean['precio'] = pd.to_numeric(df_clean['precio'], errors='coerce')
            if 'precio_adquisicion' in df_clean.columns:
                df_clean['precio_adquisicion'] = pd.to_numeric(df_clean['precio_adquisicion'], errors='coerce')
            if 'precio_venta' in df_clean.columns:
                df_clean['precio_venta'] = pd.to_numeric(df_clean['precio_venta'], errors='coerce')
            if 'stock_actual' in df_clean.columns:
                df_clean['stock_actual'] = pd.to_numeric(df_clean['stock_actual'], errors='coerce').fillna(0).astype(int)
            if 'cantidad' in df_clean.columns:
                df_clean['cantidad'] = pd.to_numeric(df_clean['cantidad'], errors='coerce').fillna(1).astype(int)

            # --- Tarea de Limpieza IA (Solo para Inventario si las tallas/colores son nulos o están empotrados) ---
            if tipo == "Inventario":
                 # Supongamos que si la columna 'color' y 'talla' están ambas llenas de Nulos
                 # Significa que no subió esas columnas porque las empotró en el nombre.
                 # Desempaquetemos usando Gemini.
                 
                 necesita_ia = df_clean['talla'].isna().all() and df_clean['color'].isna().all()
                 # Para no agobiar el API, extraigamos si hay menos de 50 filas únicas (por seguridad del MVP)
                 if necesita_ia and len(df_clean) <= 100:
                     unique_names = df_clean['producto'].dropna().unique().tolist()
                     extracted_data = extract_product_attributes_batch(unique_names).get("data", [])
                     
                     # Re-asignar desempaquetado al dataframe
                     extract_dict = {item['original']: item for item in extracted_data if isinstance(item, dict) and 'original' in item}
                     
                     def apply_ai_extract(row, target_col):
                         name = row['producto']
                         if name in extract_dict:
                             return extract_dict[name].get(target_col, row[target_col])
                         return row[target_col]
                         
                     df_clean['talla'] = df_clean.apply(lambda r: apply_ai_extract(r, 'talla'), axis=1)
                     df_clean['color'] = df_clean.apply(lambda r: apply_ai_extract(r, 'color'), axis=1)
                     df_clean['producto_original'] = df_clean['producto'] # back up the long name
                     df_clean['producto'] = df_clean.apply(lambda r: apply_ai_extract(r, 'producto_base'), axis=1)

        # Guardar en estado final listo para previsualizar
        st.session_state.cleaned_dataframe = df_clean
    
    # 2. Renderizar st.data_editor para permitir correcciones humanas de los NA/rojos
    st.info("Revisa la matriz y corrige cualquier celda resaltada en **ROJO** (Datos faltantes o incompatibles).")
    
    current_df = st.session_state.cleaned_dataframe
    styled_df = current_df.style.map(highlight_invalid_cells)
    
    # Render interactive grid!
    edited_df = st.data_editor(
         styled_df,
         use_container_width=True,
         num_rows="dynamic",
         key="data_editor_bulk"
    )
    
    # Evaluar si la grilla tiene errores
    has_errors = edited_df.isna().any().any() # Si tiene NA's crudos sin resolver
    
    # Validacion estricta específica
    if tipo == "Inventario" and edited_df['producto'].isna().any():
         has_errors = True
    elif tipo == "Ventas" and (edited_df['producto'].isna().any() or edited_df['precio'].isna().any()):
         has_errors = True
         
    st.divider()
    
    col_submit = st.columns([1, 1, 1])
    with col_submit[1]:
        if has_errors:
             st.warning("⚠️ Debes corregir todas las celdas nulas obligatorias resaltadas para poder guardar.")
             st.button("Guardar en Base de Datos", disabled=True, type="primary")
        else:
             if st.button("🚀 Guardar en Base de Datos", disabled=False, type="primary"):
                  with st.spinner("Realizando Resolución de Entidades e Inserción Segura..."):
                       # Convert DataFrame back to list of dicts for our db functions
                       records = edited_df.to_dict('records')
                       
                       res = None
                       if tipo == "Inventario":
                            res = upsert_inventory_bulk(records)
                       else:
                            res = resolve_and_insert_sales_bulk(records)
                            
                       if res and res.get("success"):
                            st.success(f"🎉 {dict(res).get('message', 'Operación exitosa')}")
                            # Clean states
                            st.session_state.mass_upload_step = 1
                            if 'gemini_suggestions' in st.session_state: del st.session_state.gemini_suggestions
                            if 'cleaned_dataframe' in st.session_state: del st.session_state.cleaned_dataframe
                       else:
                            st.error(f"Error bloqueante en DB: {res.get('message')}")

def render_mass_upload_tab():
    if 'mass_upload_step' not in st.session_state:
        st.session_state.mass_upload_step = 1
        st.session_state.mass_upload_tipo = None
    
    st.title("📂 Subida Inteligente por Lotes de Excel")
    
    step = st.session_state.mass_upload_step
    if step == 1:
         render_paso1_seleccion()
    elif step == 2:
         render_paso2_mapeador()
    elif step == 3:
         render_paso3_validacion()
