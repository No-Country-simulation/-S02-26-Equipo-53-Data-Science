import streamlit as st
import sys
import os

# Configuración de página - Debe ser lo primero
st.set_page_config(
    page_title="Gestión Dueño - Control Center",
    page_icon="👨‍💼",
    layout="wide"
)

# Forzar ruta absoluta al root del proyecto para resolver dependencias
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

try:
    from modules.gestion_dueño.app import main
    main()
except Exception as e:
    st.error(f"Error al cargar el módulo de Gestión: {e}")
    import traceback
    st.code(traceback.format_exc())
