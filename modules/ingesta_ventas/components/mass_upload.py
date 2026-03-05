import streamlit as st
import pandas as pd
import io
from modules.ingesta_ventas.services.extraction_service import suggest_column_mapping
from modules.ingesta_ventas.services.db_service import upsert_inventory_bulk, resolve_and_insert_sales_bulk, check_product_ambiguity, get_product_id
from libs.logger import logError, logInfo
from libs.db_connection import get_db_connection
import os
import re

# Definir la estructura obligatoria que requiere la base de datos
TEMPLATE_INVENTARIO = ["producto", "categoria", "talla", "color", "stock_actual", "precio_adquisicion", "precio_venta"]

# Columnas Requeridas vs Opcionales para Ventas
REQUIRED_VENTAS = ["producto", "cantidad", "precio"]
OPTIONAL_VENTAS = ["nombre_cliente", "medio_pago", "fecha_registro", "talla", "color", "categoria"]
TEMPLATE_VENTAS = REQUIRED_VENTAS + OPTIONAL_VENTAS

TEMPLATE_CLIENTES = ["nombre_cliente", "ubicacion_cliente", "genero"]

def download_template_btn(tipo: str):
    """Genera un botón funcional para descargar un CSV de plantilla salvavidas."""
    if tipo == "Inventario": cols = TEMPLATE_INVENTARIO
    elif tipo == "Ventas": cols = TEMPLATE_VENTAS
    else: cols = TEMPLATE_CLIENTES
    df_template = pd.DataFrame(columns=cols)
    
    # Extraemos el CSV crudo al instante para que Streamlit guarde en caché los bytes
    # y no pierda la referencia (MediaFileStorageError)
    csv_bytes = df_template.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label=f"⬇️ Descargar Plantilla '{tipo}' (Recomendado)",
        data=csv_bytes,
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

    # Fila 3: Carga Técnica (Backup)
    st.divider()
    with st.container(border=True):
        cc1, cc2 = st.columns([0.7, 0.3])
        with cc1:
            st.markdown("### 🛠️ Carga Técnica (Backup Directo)")
            st.write("Solo para datos que ya tienen la estructura exacta de la base de datos (con IDs calculados). Evita validaciones de la IA e inyecta directamente a la tabla Raw.")
        with cc2:
            if st.button("⚠️ Cargar Backup", type="secondary", width="stretch"):
                st.session_state.mass_upload_tipo = "Backup"
                st.session_state.mass_upload_step = "backup"
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
                st.markdown("#### 🚩 Columnas Obligatorias")
                for req_col in REQUIRED_VENTAS if tipo == "Ventas" or (tipo == "Smart" and st.session_state.get("mass_upload_target") == "Ventas") else expected_cols:
                    default_idx = 0
                    if req_col in sug_map:
                         try: default_idx = opciones_select.index(sug_map[req_col])
                         except ValueError: pass 
                    
                    st.selectbox(f"Columna para **'{req_col}'** (Obligatorio)", options=opciones_select, index=default_idx, key=f"map_{req_col}")
                    current_mapping[req_col] = st.session_state[f"map_{req_col}"]

                if tipo == "Ventas" or (tipo == "Smart" and st.session_state.get("mass_upload_target") == "Ventas"):
                    st.markdown("#### ℹ️ Columnas Opcionales (La IA intentará resolverlas si faltan)")
                    for opt_col in OPTIONAL_VENTAS:
                        default_idx = 0
                        if opt_col in sug_map:
                             try: default_idx = opciones_select.index(sug_map[opt_col])
                             except ValueError: pass 
                        
                        st.selectbox(f"Columna para **'{opt_col}'** (Opcional)", options=opciones_select, index=default_idx, key=f"map_{opt_col}")
                        current_mapping[opt_col] = st.session_state[f"map_{opt_col}"]
                    
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

            # --- Limpieza Estructurada (REGEX) ---
            if tipo in ["Inventario", "Ventas", "Smart"]:
                st.write("🔍 Extrayendo atributos de nombres de productos (Regex)...")
                
                def extract_attributes_deterministic(row):
                    name = str(row['producto'])
                    talla = row.get('talla')
                    color = row.get('color')
                    
                    # 1. Extraer Talla si es nula
                    if pd.isna(talla) or str(talla).strip() == "":
                        # Buscar patrones comunes de tallas (S, M, L, XL, XXL, 38, 40, etc)
                        # Buscamos tallas al final o rodeadas de espacios/guiones
                        size_match = re.search(r'\b(S|M|L|XL|XXL|XXXL|XS|3XL|2XL)\b', name, re.IGNORECASE)
                        if size_match:
                            row['talla'] = size_match.group(0).upper()
                        else:
                            # Buscar tallas numéricas (común en calzado/jeans)
                            num_match = re.search(r'\b(2[8-9]|3[0-9]|4[0-9]|5[0-6])\b', name)
                            if num_match:
                                row['talla'] = num_match.group(0)
                    
                    # 2. Extraer Color si es nulo (Opcional, basado en lista simple)
                    if pd.isna(color) or str(color).strip() == "":
                        colors = ['Negro', 'Blanco', 'Rojo', 'Azul', 'Verde', 'Amarillo', 'Gris', 'Beige', 'Rosado', 'Lila', 'Marrón']
                        for c in colors:
                            if re.search(rf'\b{c}\b', name, re.IGNORECASE):
                                row['color'] = c
                                break
                    return row

                df_clean = df_clean.apply(extract_attributes_deterministic, axis=1)
            
            # --- Resolviedo IDs y Verificando Ambigüedad (SÓLO PARA VENTAS) ---
            if tipo == "Ventas" or (tipo == "Smart" and st.session_state.get("mass_upload_target") == "Ventas"):
                st.write("🔍 Resolviendo IDs de producto y validando variantes...")
                conn = get_db_connection()
                schema = os.getenv("DB_SCHEMA", "raw")
                if conn:
                    with conn:
                        with conn.cursor() as cursor:
                            def smart_resolve(row):
                                name = row['producto']
                                t = row.get('talla')
                                c = row.get('color')
                                
                                # Intentar resolución directa
                                rid = get_product_id(cursor, schema, name, t, c)
                                
                                # Verificamos ambigüedad si no hay talla/color específicos
                                if not t or not c or str(t).strip() == "" or str(c).strip() == "":
                                    es_ambiguo, variantes = check_product_ambiguity(cursor, schema, name)
                                    if es_ambiguo:
                                        row['_warning'] = f"Ambiguo: {len(variantes)} variantes. Se usará la primera."
                                        row['_ambiguity'] = variantes
                                else:
                                    row['_warning'] = None
                                    
                                row['id_producto'] = rid
                                return row
                                
                            df_clean = df_clean.apply(smart_resolve, axis=1)
                    conn.close()

            st.session_state.cleaned_dataframe = df_clean
            status.update(label="✅ Pipeline completado", state="complete")

    # 2. Previsualización y Corrección Humana
    current_df = st.session_state.cleaned_dataframe
    
    # Reporte de Errores (Resumen arriba)
    missing_prods = current_df['producto'].isna().sum() if 'producto' in current_df.columns else 0
    unresolved_ids = current_df['id_producto'].isna().sum() if 'id_producto' in current_df.columns else 0
    ambiguous_count = current_df['_warning'].notna().sum() if '_warning' in current_df.columns else 0
    
    invalid_prices = 0
    if 'precio' in current_df.columns:
        invalid_prices = current_df['precio'].isna().sum()
    
    if missing_prods > 0 or unresolved_ids > 0 or invalid_prices > 0 or ambiguous_count > 0:
        with st.container(border=True):
            st.markdown("#### ⚖️ Resumen de Validación")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("⚠️ No encontrados", unresolved_ids)
            with c2: st.metric("❓ Ambiguos", ambiguous_count)
            with c3: st.metric("❌ Errores Críticos", missing_prods + invalid_prices)
            
            if ambiguous_count > 0:
                st.warning("ℹ️ **Nota sobre Ambiguos**: El sistema detectó varios productos con el mismo nombre pero distintas tallas/colores. Se asignará una por defecto, pero puedes corregirlo en el editor abajo.")
            if unresolved_ids > 0:
                st.error("❗ **Productos Faltantes**: Algunos nombres no coinciden con nada en el inventario. Deberás corregirlos o agregarlos al inventario primero.")
    else:
        st.success("✨ ¡Todo parece estar en orden! Revisa una última vez.")

    # Configuración de Columnas Estricta
    col_config = {
        "id_producto": st.column_config.NumberColumn("ID Resuelto", help="Auto-detectado por el sistema", disabled=True),
        "producto": st.column_config.TextColumn("Producto", required=True),
        "categoria": st.column_config.TextColumn("Categoría"),
        "talla": st.column_config.TextColumn("Talla (Opcional)"),
        "color": st.column_config.TextColumn("Color (Opcional)"),
        "_warning": st.column_config.TextColumn("Aviso Sistema", disabled=True),
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
    has_errors = edited_df['producto'].isna().any() if 'producto' in edited_df.columns else False
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
            data=buffer.getvalue(),  # Extraemos bytes para no corromper la caché de URL
            file_name=f"normalizado_{tipo.lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with c2:
        if st.button("🚀 Enviar a Raw", type="primary", width="stretch", disabled=has_errors):
            from modules.ingesta_ventas.services.state_manager import add_to_staging
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

            st.rerun()

def render_paso_backup():
    st.subheader("🛠️ Carga Técnica Directa (Backup Mode)")
    
    if st.button("⬅️ Volver a Paso 1", key="btn_back_backup"):
        st.session_state.mass_upload_step = 1
        st.rerun()
        
    target_table = st.selectbox("1️⃣ Selecciona la tabla de destino", ["inventario_raw", "ventas_raw", "clientes_raw"])
    
    archivo = st.file_uploader(f"2️⃣ Sube tu archivo con estructura exacta (.csv, .xlsx)", type=["csv", "xlsx"])
    
    if archivo:
        try:
            if archivo.name.endswith(".csv"): df_raw = pd.read_csv(archivo)
            else: df_raw = pd.read_excel(archivo)
                 
            st.write("📊 Previsualización de los datos crudos:")
            st.dataframe(df_raw.head(), width="stretch")
            
            st.warning("⚠️ **Advertencia:** Esta inserción se hace en crudo. Si tus columnas o tipos de datos no coinciden con la tabla de SQL, la base de datos rechazará la transacción.")
            
            if st.button("🔥 Inyectar Directamente a Base de Datos", type="primary"):
                conn = get_db_connection()
                if conn:
                    with conn:
                        from sqlalchemy import create_engine
                        from urllib.parse import quote_plus
                        from dotenv import load_dotenv
                        load_dotenv()
                        
                        db_user = os.getenv("DB_USER", "postgres")
                        db_pass = quote_plus(os.getenv("DB_PASS", ""))
                        db_host = os.getenv("DB_HOST", "localhost")
                        db_port = os.getenv("DB_PORT", "5432")
                        db_name = os.getenv("DB_NAME", "postgres")
                        db_schema = os.getenv("DB_SCHEMA", "raw")
                        
                        engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
                        
                        with st.spinner(f"Inyectando {len(df_raw)} filas en {db_schema}.{target_table}..."):
                            try:
                                df_raw.to_sql(target_table, engine, schema=db_schema, if_exists="append", index=False)
                                st.success(f"✅ ¡{len(df_raw)} filas inyectadas exitosamente en {db_schema}.{target_table}!")
                                # Pequeña pausa para que el usuario lea el éxito
                                import time
                                time.sleep(2)
                                st.session_state.mass_upload_step = 1
                                st.rerun()
                            except Exception as db_err:
                                st.error(f"❌ Error de la base de datos al inyectar: {db_err}")
                else:
                    st.error("❌ No se pudo conectar a la base de datos.")
                        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

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
    elif step == "backup":
         render_paso_backup()
