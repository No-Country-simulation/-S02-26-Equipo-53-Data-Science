import streamlit as st
import pandas as pd
from libs.logger import logInfo

def init_staging_state():
    """
    Inicializa el buffer de datos en memoria (Session State) con estructuras consistentes.
    """
    if "staging_ventas" not in st.session_state:
        st.session_state.staging_ventas = pd.DataFrame(columns=[
            "id_producto", "producto", "talla", "color", "cantidad", 
            "precio", "cliente", "medio_pago", "fecha_registro", "origen"
        ])
    
    if "staging_inventario" not in st.session_state:
        st.session_state.staging_inventario = pd.DataFrame(columns=[
            "producto", "categoria", "talla", "color", "stock_actual", 
            "precio_adquisicion", "precio_venta", "origen"
        ])

    if "staging_clientes" not in st.session_state:
        st.session_state.staging_clientes = pd.DataFrame(columns=[
            "nombre_cliente", "ubicacion_cliente", "genero", "origen"
        ])

def add_to_staging(tipo, data_list):
    """
    Añade datos al buffer de staging. 
    tipo: 'ventas', 'inventario' o 'clientes'
    """
    if not data_list:
        return

    new_df = pd.DataFrame(data_list)
    
    if tipo == "ventas":
        st.session_state.staging_ventas = pd.concat([st.session_state.staging_ventas, new_df], ignore_index=True)
    elif tipo == "inventario":
        st.session_state.staging_inventario = pd.concat([st.session_state.staging_inventario, new_df], ignore_index=True)
    elif tipo == "clientes":
        st.session_state.staging_clientes = pd.concat([st.session_state.staging_clientes, new_df], ignore_index=True)
    
    logInfo(f"Añadidos {len(new_df)} registros a Staging {tipo.capitalize()}")

def clear_staging(tipo):
    """Limpia el buffer de memoria."""
    if tipo == "ventas":
        st.session_state.staging_ventas = st.session_state.staging_ventas.iloc[0:0]
    elif tipo == "inventario":
        st.session_state.staging_inventario = st.session_state.staging_inventario.iloc[0:0]
    elif tipo == "clientes":
        st.session_state.staging_clientes = st.session_state.staging_clientes.iloc[0:0]
