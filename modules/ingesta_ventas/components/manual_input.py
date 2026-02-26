import streamlit as st
import pandas as pd
from ..services.db_service import (
    get_inventory_summary, 
    get_product_variants, 
    get_all_clients,
    insert_new_client,
    insert_sales_to_db
)
from libs.logger import logError, logInfo

@st.dialog("Agregar al Carrito")
def modal_seleccion_variante(producto_elegido):
    st.markdown(f"### {producto_elegido}")
    
    variantes = get_product_variants(producto_elegido)
    
    if not variantes:
        st.error("No hay stock disponible para este producto.")
        return
        
    df_variantes = pd.DataFrame(variantes)
    
    # Selectores lógicos dependientes
    col1, col2 = st.columns(2)
    with col1:
        colores_disponibles = df_variantes['color'].dropna().unique().tolist()
        color_seleccionado = st.selectbox("Color", options=colores_disponibles if colores_disponibles else ["Único"])
    
    with col2:
        # Filtrar tallas por el color seleccionado
        if color_seleccionado != "Único" and 'color' in df_variantes.columns:
            tallas_disp = df_variantes[df_variantes['color'] == color_seleccionado]['talla'].dropna().unique().tolist()
        else:
            tallas_disp = df_variantes['talla'].dropna().unique().tolist()
            
        talla_seleccionada = st.selectbox("Talla", options=tallas_disp if tallas_disp else ["Única"])
    
    # Encontrar la variante exacta para determinar stock y precio base
    variante_exacta = df_variantes.copy()
    if color_seleccionado != "Único" and 'color' in variante_exacta.columns:
        variante_exacta = variante_exacta[variante_exacta['color'] == color_seleccionado]
    if talla_seleccionada != "Única" and 'talla' in variante_exacta.columns:
        variante_exacta = variante_exacta[variante_exacta['talla'] == talla_seleccionada]
        
    if variante_exacta.empty:
        st.warning("Esa combinación no tiene stock.")
        return
        
    variante_info = variante_exacta.iloc[0]
    stock_maximo = int(variante_info['stock_actual'])
    precio_base = float(variante_info['precio_venta_unitario']) if pd.notnull(variante_info['precio_venta_unitario']) else 0.0

    st.write(f"**Stock disponible:** {stock_maximo}")
    
    col3, col4 = st.columns(2)
    with col3:
        cantidad = st.number_input("Cantidad", min_value=1, max_value=max(1, stock_maximo), step=1)
    with col4:
        # El precio_venta_unitario ahora se arrastra del inventario y no se puede guardar un override en la transacción
        precio_venta = st.number_input("Precio de Venta (S/)", value=precio_base, disabled=True, help="El precio base se ha predefinido en el inventario.")
        
    if st.button("Añadir", type="primary", use_container_width=True):
        nuevo_item = {
            "producto": producto_elegido,
            "categoria": st.session_state.current_cat, # Pasado por estado antes de abrir
            "talla": talla_seleccionada if talla_seleccionada != "Única" else None,
            "color": color_seleccionado if color_seleccionado != "Único" else None,
            "cantidad": cantidad,
            "precio": precio_venta
        }
        st.session_state.carrito.append(nuevo_item)
        st.toast(f"✅ Añadido: {producto_elegido}")
        st.rerun()

def render_matriz_productos():
    st.subheader("📦 Matriz de Productos")
    
    # Buscador dinámico
    search_query = st.text_input("🔍 Buscar producto por nombre...", "")
    
    productos_resumen = get_inventory_summary()
    if not productos_resumen:
        st.info("No hay productos inventariados con stock mayor a cero.")
        return
        
    df_prod = pd.DataFrame(productos_resumen)
    
    if search_query:
        df_prod = df_prod[df_prod['producto'].str.contains(search_query, case=False, na=False)]
        
    if df_prod.empty:
        st.warning("No se encontraron productos.")
        return
        
    # Filtrar por categorías (Opcional, mediante radio buttons o pills)
    categorias = ["Todas"] + df_prod['categoria'].unique().tolist()
    cat_seleccionada = st.pills("Categoría", categorias, default="Todas")
    
    if cat_seleccionada and cat_seleccionada != "Todas":
        df_prod = df_prod[df_prod['categoria'] == cat_seleccionada]

    # Dibujar la Grilla
    cols_per_row = 4
    for i in range(0, len(df_prod), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(df_prod):
                producto = df_prod.iloc[i + j]
                nombre = producto['producto']
                stock = producto['total_stock']
                cat = producto['categoria']
                
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"**{nombre}**")
                        st.caption(f"Stock total: {stock}")
                        if st.button("➕ Seleccionar", key=f"btn_{nombre}"):
                            st.session_state.current_cat = cat
                            modal_seleccion_variante(nombre)

def render_checkout_y_cliente():
    st.subheader("🛒 Resumen de Compra")
    
    if not st.session_state.carrito:
        st.info("El carrito está vacío. Selecciona productos de la matriz izquierda.")
        return
        
    df_carrito = pd.DataFrame(st.session_state.carrito)
    
    # Editor de carrito interactivo para que puedan borrar
    edited_carrito = st.data_editor(
        df_carrito,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "producto": st.column_config.TextColumn("Producto", disabled=True),
            "cantidad": st.column_config.NumberColumn("Cant.", min_value=1),
            "precio": st.column_config.NumberColumn("Precio", format="S/ %.2f")
        }
    )
    
    st.session_state.carrito = edited_carrito.to_dict('records')
    
    # Calcular Total
    if st.session_state.carrito:
        total = sum([float(item.get('precio', 0)) * int(item.get('cantidad', 1)) for item in st.session_state.carrito])
        st.markdown(f"### 💰 Total a Pagar: S/ {total:.2f}")
    
    st.divider()
    
    st.subheader("👤 Datos del Cliente")
    
    clientes = get_all_clients()
    opciones_cliente = ["-- Seleccionar Existente --"]
    dict_clientes = {}
    
    for c in clientes:
        label = f"{c['nombre_cliente']}"
        opciones_cliente.append(label)
        dict_clientes[label] = c
        
    cliente_seleccionado = st.selectbox("Buscar Cliente Frecuente", options=opciones_cliente)
    
    with st.expander("➕ O Crear Nuevo Cliente"):
        with st.form("form_nuevo_cliente"):
            n_nombre = st.text_input("Nombre Completo o Razón Social")
            n_ubicacion = st.selectbox("Ubicación", ["Desconocido", "Arequipa", "Lima", "Puno", "Cusco", "Tacna", "Moquegua"])
            n_genero = st.radio("Género", ["M", "F", "U"], horizontal=True)
            
            submit_cliente = st.form_submit_button("Guardar Cliente")
            if submit_cliente:
                if n_nombre.strip() == "":
                    st.error("El nombre es obligatorio")
                else:
                    res = insert_new_client({
                        "nombre_cliente": n_nombre,
                        "ubicacion_cliente": n_ubicacion,
                        "genero": n_genero
                    })
                    if res["success"]:
                        st.success("Cliente creado. Por favor búscalo en la lista superior.")
                        st.rerun()
                    else:
                        st.error("Error al crear cliente.")
                        
    st.divider()
    st.subheader("💳 Medio de Pago")
    medio_pago = st.radio("Selecciona un medio de pago (Obligatorio)", 
                          ["Efectivo", "Yape", "Plin", "Tarjeta", "Transferencia"], horizontal=True)
                          
    if st.button("🚀 Confirmar Venta", type="primary", use_container_width=True):
        nombre_cli_final = "Anónimo"
        if cliente_seleccionado != "-- Seleccionar Existente --":
             nombre_cli_final = dict_clientes[cliente_seleccionado]['nombre_cliente']
             
        # Preparar data para el insert
        sales_to_insert = []
        import datetime
        hoy = datetime.date.today().strftime("%Y-%m-%d")
        
        for item in st.session_state.carrito:
            sales_to_insert.append({
                "producto": item["producto"],
                "categoria": item.get("categoria"),
                "talla": item.get("talla"),
                "color": item.get("color"),
                "cantidad": item["cantidad"],
                "precio": float(item["precio"]),
                "nombre_cliente": nombre_cli_final,
                "medio_pago": medio_pago,
                "fecha_registro": hoy
            })
            
        res_insert = insert_sales_to_db(sales_to_insert)
        if res_insert["success"]:
            st.success(f"🎉 Venta guardada correctamente. {res_insert['message']}")
            st.session_state.carrito = [] # Limpiar carrito
            import time
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"Error al procesar la venta: {res_insert['message']}")

def render_manual_input_tab():
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    if 'current_cat' not in st.session_state:
        st.session_state.current_cat = None
        
    col_left, col_right = st.columns([0.65, 0.35])
    
    with col_left:
        render_matriz_productos()
        
    with col_right:
        with st.container(border=True):
            render_checkout_y_cliente()
