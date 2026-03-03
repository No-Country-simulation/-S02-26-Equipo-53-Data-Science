import streamlit as st
import sys
import os

# Configuración de página - Debe ser lo primero
st.set_page_config(
    page_title="Gestión Dueño - Control Center",
    page_icon="👨‍💼",
    layout="wide"
)

# Añadir la raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from modules.gestion_dueño.app import main
    main()
except Exception as e:
    st.error(f"Error al cargar el módulo de Gestión: {e}")
    import traceback
    st.code(traceback.format_exc())
