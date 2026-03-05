import streamlit as st
import datetime
from streamlit_mic_recorder import speech_to_text
from libs.logger import logInfo, logError, logSequence, logWarn
from modules.ingesta_ventas.services.extraction_service import extract_sales_data
from modules.ingesta_ventas.services.db_service import search_inventory_fuzzy
from modules.ingesta_ventas.services.state_manager import add_to_staging

def voice_input_component(key="voice_input", language="es-ES"):
    """
    Asistente de Voz Premium: Consolidado y Responsivo.
    """
    logSequence("Iniciando Asistente de Voz", key)
    # --- CSS Inyectado para Estética Premium ---
    st.markdown("""
        <style>
        div.stButton > button.st-key-btn_ia {
            background: linear-gradient(135deg, #FF4B4B, #FF8F8F);
            color: white !important;
            border: none;
            font-weight: bold;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        div.stButton > button.st-key-btn_ia:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
        }
        div.stButton > button.st-key-btn_ia:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Inicialización de Estado ---
    t_key = f"{key}_text_input"
    if t_key not in st.session_state:
        st.session_state[t_key] = ""
    if 'voice_state' not in st.session_state:
        st.session_state.voice_state = "idle" # idle, reviewing
    if 'voice_extracted_items' not in st.session_state:
        st.session_state.voice_extracted_items = []
        
    # LOGICA DE LIMPIEZA POST-EXITO (Debe ser antes de instanciar el widget)
    if st.session_state.get('voice_pending_clear'):
        st.session_state[t_key] = ""
        st.session_state.voice_pending_clear = False

    with st.container(border=True):
        st.markdown("#### 📝 Detalle del Pedido")
        
        # Creamos un placeholder para el text_area para que aparezca arriba visualmente
        # pero lo instanciaremos después de procesar los botones para poder modificar su state.
        text_area_placeholder = st.empty()
        
        # Grilla de Controles
        c1, c2, c3 = st.columns([1, 1, 1.2])
        
        with c1:
            # Captura de Audio
            audio_text = speech_to_text(
                language=language,
                start_prompt="🎤 Dictar",
                stop_prompt="⏹️ Grabar",
                just_once=True, 
                use_container_width=True,
                key=f"{key}_recorder"
            )
            
            # Lógica de Actualización: DEBE ocurrir antes de instanciar el widget
            if audio_text:
                current_text = st.session_state.get(t_key, "")
                st.session_state[t_key] = (current_text + " " + audio_text).strip()

        with c2:
            if st.button("🗑️ Limpiar", width="stretch", key=f"{key}_clear"):
                st.session_state[t_key] = ""
                st.session_state.voice_state = "idle"
                st.session_state.voice_extracted_items = []
                st.rerun()

        with c3:
            current_val = st.session_state.get(t_key, "")
            if st.button("🚀 Analizar con IA", key="btn_ia", width="stretch", disabled=not current_val):
                st.session_state.voice_state = "processing"

        # AHORA instanciamos el text_area en el placeholder
        text_area_placeholder.text_area(
            "Escribe o dicta lo vendido:",
            placeholder="Ej: Vendí 3 polos verdes talla M a 45 soles...",
            height=150,
            key=t_key,
            label_visibility="collapsed"
        )

    # --- Lógica de Procesamiento IA ---
    if st.session_state.voice_state == "processing":
        with st.status("🔮 Gemini está interpretando tu pedido...", expanded=False) as status:
            logSequence("Procesando audio/texto con Gemini")
            res = extract_sales_data(st.session_state[t_key])
            if "data" in res:
                logInfo(f"IA extrajo {len(res['data'])} items")
                resolved_items = []
                for item in res["data"]:
                    name_base = item.get("producto_base") or item.get("producto_dictado", "")
                    # Reducimos a 3 alternativas sugeridas para no saturar la UI
                    matches = search_inventory_fuzzy(name_base, limit=3)
                    
                    if matches:
                        # Lógica de pre-selección de variante basada en lo que la IA extrajo
                        best_match_idx = 0
                        best_var_idx = 0
                        
                        target_talla = str(item.get("talla")).lower() if item.get("talla") else None
                        target_color = str(item.get("color")).lower() if item.get("color") else None
                        
                        # Intentar encontrar la variante que coincida con lo extraído
                        found_var = False
                        for m_idx, match in enumerate(matches):
                            for v_idx, var in enumerate(match["variantes"]):
                                v_talla = str(var.get("talla")).lower()
                                v_color = str(var.get("color")).lower()
                                if (target_talla and target_talla in v_talla) or (target_color and target_color in v_color):
                                    best_match_idx = m_idx
                                    best_var_idx = v_idx
                                    found_var = True
                                    break
                            if found_var: break

                        resolved_items.append({
                            "original": name_base,
                            "matches": matches,
                            "selected_match_idx": best_match_idx,
                            "selected_variant_idx": best_var_idx,
                            "cantidad": item.get("cantidad", 1),
                            "precio_dictado": item.get("precio", 0.0),
                            "talla_ia": item.get("talla"),
                            "color_ia": item.get("color"),
                            "nombre_cliente": item.get("nombre_cliente"),
                            "ubicacion_cliente": item.get("ubicacion_cliente"),
                            "medio_pago": item.get("medio_pago"),
                            "fecha_registro": item.get("fecha_registro"),
                            "status": "Match Encontrado",
                            "validado": True if found_var else False # Si encontramos variante exacta, pre-validamos
                        })
                    else:
                        logWarn(f"No se encontraron coincidencias para: {name_base}")
                        resolved_items.append({
                            "original": name_base,
                            "matches": [],
                            "producto": "No encontrado",
                            "status": "No Encontrado",
                            "validado": False
                        })
                
                st.session_state.voice_extracted_items = resolved_items
                st.session_state.voice_state = "reviewing"
                status.update(label=f"✅ Análisis completado ({res.get('model', 'IA')})", state="complete")
                st.rerun()
            else:
                st.session_state.voice_state = "idle"
                st.error("No se pudo extraer información del texto.")

    # --- UI de Confirmación (Resultados con Validación) ---
    if st.session_state.voice_state == "reviewing" and st.session_state.voice_extracted_items:
        st.markdown("### 📋 Validación de Pedido IA")
        st.caption("Verifica y ajusta los productos antes de enviarlos al carrito.")
        
        for i, item in enumerate(st.session_state.voice_extracted_items):
            with st.container(border=True):
                if item["status"] == "Match Encontrado":
                    # --- Header de la Card ---
                    cols_h = st.columns([0.8, 0.2])
                    with cols_h[0]:
                        st.markdown(f"**Item {i+1}:** Dictado: _{item['original']}_")
                    with cols_h[1]:
                        st.session_state.voice_extracted_items[i]["validado"] = st.checkbox(
                            "Confirmar", key=f"vb_{i}", value=item.get("validado", False)
                        )

                    # --- Selector de Producto (Sugerencias IA + Fallback Manual) ---
                    matches = item["matches"]
                    match_names = [m["producto_oficial"] for m in matches]
                    
                    # Añadimos la opción de búsqueda manual al final
                    options_display = match_names + ["🔍 Buscar manualmente..."]
                    
                    selected_match_idx = st.selectbox(
                        "Producto detectado (Sugerencias IA):",
                        options=range(len(options_display)),
                        format_func=lambda x: options_display[x],
                        key=f"match_sel_{i}",
                        index=item["selected_match_idx"]
                    )
                    st.session_state.voice_extracted_items[i]["selected_match_idx"] = selected_match_idx
                    
                    # Lógica de fallback manual
                    is_manual = (selected_match_idx == len(match_names))
                    
                    if is_manual:
                        # Obtenemos todo el inventario resumido para el buscador manual
                        from modules.ingesta_ventas.services.db_service import get_inventory_summary, get_product_variants
                        all_inventory = get_inventory_summary()
                        all_names = [p["producto"] for p in all_inventory]
                        
                        manual_prod_name = st.selectbox(
                            "Selecciona el producto del catálogo:",
                            options=all_names,
                            key=f"manual_sel_{i}"
                        )
                        
                        # Al elegir manualmente, cargamos sus variantes reales
                        current_match = {
                            "producto_oficial": manual_prod_name,
                            "variantes": get_product_variants(manual_prod_name)
                        }
                    else:
                        current_match = matches[selected_match_idx]

                    # --- Selector de Variante ---
                    variantes = current_match["variantes"]
                    
                    if variantes:
                        # Si solo hay una variante, la seleccionamos por defecto
                        var_options = []
                        for v in variantes:
                            label = f"{v.get('talla', 'N/A')} | {v.get('color', 'N/A')} (S/ {v.get('precio', 0):.2f}) - Stock: {v.get('stock_actual', 0)}"
                            var_options.append(label)
                        
                        selected_variant_idx = st.selectbox(
                            "Selecciona Talla/Color:",
                            options=range(len(var_options)),
                            format_func=lambda x: var_options[x],
                            key=f"var_sel_{i}",
                            index=min(item["selected_variant_idx"], len(var_options)-1)
                        )
                        st.session_state.voice_extracted_items[i]["selected_variant_idx"] = selected_variant_idx
                        
                        # Datos finales de la variante elegida
                        chosen_var = variantes[selected_variant_idx]
                        
                        # --- Métricas Rápidas ---
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            # Aseguramos que los valores no sean None para evitar TypeError
                            cant = item.get('cantidad', 1)
                            if cant is None: cant = 0
                            
                            stock = chosen_var.get('stock_actual', 0)
                            if stock is None: stock = 0
                            
                            color_stock = "green" if cant <= stock else "red"
                            st.markdown(f"📦 **Stock:** :{color_stock}[{stock}] ({'✅' if cant <= stock else '⚠️'})")
                        with c2:
                            p_dictado = item.get('precio_dictado')
                            p_oficial = chosen_var.get('precio', 0.0)
                            
                            # Validamos que p_dictado no sea None antes de comparar
                            if p_dictado is not None and p_dictado > 0 and abs(p_dictado - p_oficial) > 0.01:
                                st.markdown(f"💰 **Precio:** :orange[S/ {p_dictado:.2f}] (vs S/ {p_oficial:.2f})")
                            else:
                                st.markdown(f"💰 **Precio:** S/ {p_oficial:.2f}")
                        with c3:
                            new_cant = st.number_input("Cant:", min_value=1, value=max(1, int(cant)), key=f"cant_input_{i}")
                            st.session_state.voice_extracted_items[i]["cantidad"] = new_cant

                        # --- CLIENTE Y MEDIO DE PAGO ---
                        st.divider()
                        cc1, cc2 = st.columns(2)
                        
                        with cc1:
                            # Selector Inteligente de Cliente
                            from modules.ingesta_ventas.services.db_service import get_all_clients
                            all_clients = get_all_clients()
                            client_names = [c["nombre_cliente"] for c in all_clients]
                            
                            default_client = item.get("nombre_cliente") or "Anónimo"
                            # Si la IA extrajo algo, lo buscamos en la lista o lo añadimos como "Nuevo"
                            if default_client not in client_names and default_client != "Anónimo":
                                client_names.insert(0, f"🆕 Crear: {default_client}")
                            elif "Anónimo" not in client_names:
                                client_names.append("Anónimo")
                            
                            try:
                                initial_idx = client_names.index(f"🆕 Crear: {default_client}") if f"🆕 Crear: {default_client}" in client_names else client_names.index(default_client)
                            except ValueError:
                                initial_idx = 0
                                
                            sel_client = st.selectbox(
                                "👤 Cliente:",
                                options=client_names,
                                key=f"client_sel_{i}",
                                index=initial_idx
                            )
                            # Guardamos en el estado interno del item
                            st.session_state.voice_extracted_items[i]["cliente_final"] = sel_client

                        with cc2:
                            # Selector de Medio de Pago
                            pagos_disponibles = ["Efectivo", "Yape", "Plin", "Tarjeta", "Transferencia"]
                            ia_pago = item.get("medio_pago")
                            
                            try:
                                p_idx = pagos_disponibles.index(ia_pago) if ia_pago in pagos_disponibles else 0
                            except ValueError:
                                p_idx = 0
                                
                            sel_pago = st.selectbox(
                                "💳 Pago:",
                                options=pagos_disponibles,
                                key=f"pago_sel_{i}",
                                index=p_idx
                            )
                            st.session_state.voice_extracted_items[i]["pago_final"] = sel_pago
                    else:
                        st.warning("No se encontraron variantes disponibles para este producto.")
                    
                else:
                    st.error(f"**Item {i+1}: Producto No Identificado**")
                    st.write(f"Texto original: _{item['original']}_")
                    st.warning("Intenta corregir el texto o búscalo manualmente.")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.button("🔄 Corregir Texto", width="stretch"):
                st.session_state.voice_state = "idle"
                st.rerun()
        with col_f2:
            items_para_carrito_indices = [idx for idx, it in enumerate(st.session_state.voice_extracted_items) if it.get("validado")]
            label_btn = f"🛒 Añadir {len(items_para_carrito_indices)} items al Carrito"
            
            if st.button(label_btn, type="primary", width="stretch", disabled=not items_para_carrito_indices):
                if 'carrito' not in st.session_state: st.session_state.carrito = []
                temp_items = []
                
                for idx in items_para_carrito_indices:
                    it = st.session_state.voice_extracted_items[idx]
                    
                    # 1. Recuperar qué se seleccionó finalmente (IA o Manual)
                    match_idx = st.session_state.get(f"match_sel_{idx}", it["selected_match_idx"])
                    var_idx = st.session_state.get(f"var_sel_{idx}", it["selected_variant_idx"])
                    
                    is_manual = (match_idx == len(it["matches"]))
                    
                    if is_manual:
                        # Recuperar selección manual del SELECTBOX
                        prod_name = st.session_state.get(f"manual_sel_{idx}")
                        if not prod_name: continue
                        
                        from modules.ingesta_ventas.services.db_service import get_product_variants
                        variantes = get_product_variants(prod_name)
                        if not variantes: continue
                        
                        var_idx = min(var_idx, len(variantes) - 1)
                        chosen_var = variantes[var_idx]
                        chosen_match_name = prod_name
                    else:
                        chosen_match = it["matches"][match_idx]
                        chosen_match_name = chosen_match["producto_oficial"]
                        chosen_var = chosen_match["variantes"][var_idx]

                    p_dictado = it.get("precio_dictado")
                    precio_final = p_dictado if (p_dictado is not None and p_dictado > 0) else chosen_var["precio"]

                    # 2. Añadir a la lista temporal para Staging
                    temp_items.append({
                        "id_producto": chosen_var["id_producto"],
                        "producto": chosen_match_name,
                        "talla": chosen_var["talla"],
                        "color": chosen_var["color"],
                        "cantidad": it.get("cantidad", 1),
                        "precio": precio_final,
                        "cliente": it.get("cliente_final", "Anónimo"),
                        "ubicacion_cliente": it.get("ubicacion_cliente", "Desconocido"),
                        "medio_pago": it.get("pago_final", "Efectivo"),
                        "fecha_registro": it.get("fecha_registro") or datetime.date.today().strftime("%Y-%m-%d"),
                        "origen": "Voz/IA",
                        "categoria": chosen_var.get("categoria")
                    })
                
                # Enviamos todo al Raw Area Global
                add_to_staging("ventas", temp_items)
                
                st.toast(f"✅ {len(temp_items)} items enviados a Revisión (Staging)")
                # NOTA: Usamos un flag para limpiar el texto en el SIGUIENTE run antes de instanciar el widget
                st.session_state.voice_pending_clear = True
                st.session_state.voice_state = "idle"
                st.session_state.voice_extracted_items = []
                st.rerun()
