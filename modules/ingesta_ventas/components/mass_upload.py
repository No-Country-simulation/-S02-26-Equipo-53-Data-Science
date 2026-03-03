import streamlit as st
import pandas as pd
import io
from ..services.extraction_service import suggest_column_mapping, extract_product_attributes_batch
from ..services.db_service import upsert_inventory_bulk, resolve_and_insert_sales_bulk
from libs.logger import logError, logInfo

# Definir la estructura obligatoria que requiere la base de datos
TEMPLATE_INVENTARIO = ["producto", "categoria", "talla", "color", "stock_actual", "precio_adquisicion", "precio_venta"]
TEMPLATE_VENTAS = ["producto", "cantidad", "precio", "nombre_cliente", "medio_pago", "fecha_registro"]
TEMPLATE_CLIENTES = ["nombre_cliente", "ubicacion_cliente", "genero"]

def download_template_btn(tipo: str):
    """Genera un botón funcional para descargar un CSV de plantilla salvavidas."""
    if tipo == "Inventario": cols = TEMPLATE_INVENTARIO
    elif tipo == "Ventas": cols = TEMPLATE_VENTAS
    else: cols = TEMPLATE_CLIENTES
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
        width="stretch"
    )

def highlight_invalid_cells(val):
    """Pandas Styler: Pinta de rojo si un valor esperado estricto está vacío o es inválido"""
    if pd.isna(val) or val == "" or str(val).strip() == "":
         return 'background-color: #ffcccc; color: #900000;'
    return ''

def render_paso1_seleccion():
    st.subheader("Paso 1: ¿Qué deseas cargar?")
    
    # Fila 1: Estándares
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### 📦 Inventario")
            download_template_btn("Inventario")
            if st.button("Subir Inventario", key="btn_sel_inv", width="stretch"):
                st.session_state.mass_upload_tipo = "Inventario"
                st.session_state.mass_upload_step = 2
                st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown("### 📈 Ventas")
            download_template_btn("Ventas")
            if st.button("Subir Ventas", key="btn_sel_ven", width="stretch"):
                 st.session_state.mass_upload_tipo = "Ventas"
                 st.session_state.mass_upload_step = 2
                 st.rerun()
    with c3:
        with st.container(border=True):
            st.markdown("### 👥 Clientes")
            download_template_btn("Clientes")
            if st.button("Subir Clientes", key="btn_sel_cli", width="stretch"):
                 st.session_state.mass_upload_tipo = "Clientes"
                 st.session_state.mass_upload_step = 2
                 st.rerun()

    # Fila 2: El Inteligente
    st.divider()
    with st.container(border=True):
        cc1, cc2 = st.columns([0.7, 0.3])
        with cc1:
            st.markdown("### 🧠 Mapeador Inteligente (IA)")
            st.write("Sube cualquier archivo (sin importar las columnas) y deja que Gemini lo organice por ti.")
        with cc2:
            if st.button("🚀 Iniciar Mapper IA", type="primary", width="stretch"):
                st.session_state.mass_upload_tipo = "Smart"
                st.session_state.mass_upload_step = 2
                st.rerun()

def render_paso2_mapeador():
    tipo = st.session_state.mass_upload_tipo
    st.subheader(f"Paso 2: Subir y Mapear ({tipo})")
    
    if st.button("⬅️ Volver a Paso 1", key="btn_back_1"):
        st.session_state.mass_upload_step = 1
        st.rerun()
        
    archivo = st.file_uploader(f"Sube tu archivo (.csv, .xlsx)", type=["csv", "xlsx"])
    
    if archivo:
        try:
            if archivo.name.endswith(".csv"): df_raw = pd.read_csv(archivo)
            else: df_raw = pd.read_excel(archivo)
                 
            st.session_state.mass_upload_file = df_raw
            raw_cols = df_raw.columns.tolist()

            # En modo Smart, primero preguntamos a qué tabla apunta
            if tipo == "Smart":
                target_table = st.radio("¿A qué tabla corresponden estos datos?", ["Inventario", "Ventas", "Clientes"], horizontal=True)
                st.session_state.mass_upload_target = target_table
                if target_table == "Inventario": expected_cols = TEMPLATE_INVENTARIO
                elif target_table == "Ventas": expected_cols = TEMPLATE_VENTAS
                else: expected_cols = TEMPLATE_CLIENTES
            else:
                if tipo == "Inventario": expected_cols = TEMPLATE_INVENTARIO
                elif tipo == "Ventas": expected_cols = TEMPLATE_VENTAS
                else: expected_cols = TEMPLATE_CLIENTES
            
            # Mapper Inteligente
            st.info("🤖 Analizando columnas con IA...")
            if 'gemini_suggestions' not in st.session_state:
                st.session_state.gemini_suggestions = suggest_column_mapping(raw_cols, expected_cols)
                     
            sug_map = st.session_state.gemini_suggestions.get("mapping", {})
            current_mapping = {}
            opciones_select = ["-- Faltante / Asignar Nulo --"] + raw_cols
            
            with st.form("form_mapeo"):
                for req_col in expected_cols:
                    default_idx = 0
                    if req_col in sug_map:
                         try: default_idx = opciones_select.index(sug_map[req_col])
                         except ValueError: pass 
                    
                    val_seleccionado = st.selectbox(f"Columna para **'{req_col}'**", options=opciones_select, index=default_idx)
                    current_mapping[req_col] = val_seleccionado
                    
                enviar_mapeo = st.form_submit_button("Siguiente: Limpiar y Validar", type="primary")
            
            if enviar_mapeo:
                st.session_state.mass_upload_mapping = current_mapping
                st.session_state.mass_upload_step = 3
                # Limpiar cache de IA para el siguiente paso si fuera necesario
                if 'cleaned_dataframe' in st.session_state: del st.session_state.cleaned_dataframe
                st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

        except Exception as e:
            st.error(f"No se pudo leer el archivo: {e}")

def render_paso3_validacion():
    tipo = st.session_state.mass_upload_tipo
    st.subheader(f"Paso 3: Limpieza y Validación con IA ({tipo})")
    
    col_b, col_stats = st.columns([0.3, 0.7])
    with col_b:
        if st.button("⬅️ Volver al Mapeo", key="btn_back_2"):
            st.session_state.mass_upload_step = 2
            st.rerun()

    df_raw = st.session_state.mass_upload_file
    mapping = st.session_state.mass_upload_mapping
    
    # 1. Aplicar Mapeo y Limpieza Inicial
    if 'cleaned_dataframe' not in st.session_state:
        df_clean = pd.DataFrame()
        for req_col, excel_col in mapping.items():
            if excel_col == "-- Faltante / Asignar Nulo --":
                df_clean[req_col] = None
            else:
                df_clean[req_col] = df_raw[excel_col]

        with st.status("🛠️ Ejecutando Pipeline de Limpieza...", expanded=True) as status:
            # --- Limpieza PANDAS (Tipos de Datos) ---
            st.write("Convertiendo tipos de datos...")
            for col in ['precio', 'precio_adquisicion', 'precio_venta']:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            for col in ['stock_actual', 'cantidad']:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int)

            # --- Limpieza IA (Solo si faltan atributos críticos) ---
            if tipo in ["Inventario", "Ventas", "Smart"]:
                st.write("🤖 Gemini analizando descripciones de productos...")
                necesita_ia = df_clean.get('talla', pd.Series()).isna().all() or df_clean.get('color', pd.Series()).isna().all()
                if necesita_ia and len(df_clean) <= 150:
                    unique_names = df_clean['producto'].dropna().unique().tolist()
                    extracted_data = extract_product_attributes_batch(unique_names).get("data", [])
                    
                    extract_dict = {item['original']: item for item in extracted_data if isinstance(item, dict) and 'original' in item}
                    
                    def apply_ai_extract(row, target_col):
                        name = row['producto']
                        if name in extract_dict:
                            # Priorizar valor extraído si el original es nulo
                            extracted_val = extract_dict[name].get(target_col)
                            return extracted_val if pd.isna(row[target_col]) or row[target_col] == "" else row[target_col]
                        return row[target_col]
                        
                    df_clean['talla'] = df_clean.apply(lambda r: apply_ai_extract(r, 'talla'), axis=1)
                    df_clean['color'] = df_clean.apply(lambda r: apply_ai_extract(r, 'color'), axis=1)
                    # No sobreescribimos 'producto' a menos que sea necesario para simplificar
            
            st.session_state.cleaned_dataframe = df_clean
            status.update(label="✅ Pipeline completado", state="complete")

    # 2. Previsualización y Corrección Humana
    current_df = st.session_state.cleaned_dataframe
    
    # Reporte de Errores (Resumen arriba)
    missing_prods = current_df['producto'].isna().sum()
    invalid_prices = 0
    if 'precio' in current_df.columns:
        invalid_prices = current_df['precio'].isna().sum()
    
    if missing_prods > 0 or invalid_prices > 0:
        st.error(f"⚠️ Se detectaron **{missing_prods}** productos sin nombre y **{invalid_prices}** errores de precio.")
    else:
        st.success("✨ ¡Todo parece estar en orden! Revisa una última vez.")

    # Configuración de Columnas Estricta
    col_config = {
        "producto": st.column_config.TextColumn("Producto", required=True),
        "categoria": st.column_config.TextColumn("Categoría"),
        "talla": st.column_config.TextColumn("Talla"),
        "color": st.column_config.TextColumn("Color"),
    }
    if tipo == "Inventario":
        col_config.update({
            "stock_actual": st.column_config.NumberColumn("Stock", min_value=0),
            "precio_adquisicion": st.column_config.NumberColumn("Costo (S/)", min_value=0.0, format="S/ %.2f"),
            "precio_venta": st.column_config.NumberColumn("Venta (S/)", min_value=0.0, format="S/ %.2f")
        })
    else:
        col_config.update({
            "cantidad": st.column_config.NumberColumn("Cant.", min_value=1),
            "precio": st.column_config.NumberColumn("Precio (S/)", min_value=0.0, format="S/ %.2f"),
            "categoria": st.column_config.TextColumn("Categoría")
        })

    edited_df = st.data_editor(
         current_df.style.map(highlight_invalid_cells),
         width="stretch",
         num_rows="dynamic",
         column_config=col_config,
         key="data_editor_bulk_v2"
    )
    
    # Validar antes de enviar
    has_errors = edited_df['producto'].isna().any()
    if tipo == "Ventas" and 'precio' in edited_df.columns:
        has_errors = has_errors or edited_df['precio'].isna().any()

    # Botones Finales
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Pestaña Smart: Botón de descarga de Normalizado
        buffer = io.BytesIO()
        edited_df.to_excel(buffer, index=False)
        st.download_button(
            "⬇️ Descargar Excel Normalizado",
            data=buffer,
            file_name=f"normalizado_{tipo.lower()}.xlsx",
            width="stretch"
        )

    with c2:
        if st.button("🚀 Enviar a Raw", type="primary", width="stretch", disabled=has_errors):
            from ..services.state_manager import add_to_staging
            records = edited_df.to_dict('records')
            # Inyectar origen y unificar campo cliente
            for r in records: 
                r["origen"] = f"Carga/{tipo}"
                if "nombre_cliente" in r:
                    r["cliente"] = r.pop("nombre_cliente")
            
            if tipo == "Ventas" or (tipo == "Smart" and st.session_state.get("mass_upload_target") == "Ventas"):
                add_to_staging("ventas", records)
            elif tipo == "Inventario" or (tipo == "Smart" and st.session_state.get("mass_upload_target") == "Inventario"):
                add_to_staging("inventario", records)
                
            st.success("✅ Datos enviados al Panel de Control (Raw).")
            st.session_state.mass_upload_step = 1
            if 'cleaned_dataframe' in st.session_state: del st.session_state.cleaned_dataframe
            st.rerun()

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
