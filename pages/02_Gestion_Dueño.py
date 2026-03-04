import streamlit as st
# Configuración de página - Debe ser lo primero
st.set_page_config(
    page_title="Gestión Dueño - Control Center",
    page_icon="👨‍💼",
    layout="wide"
)

try:
    from modules.gestion_dueño.app import main
    main()
except Exception as e:
    st.error(f"Error al cargar el módulo de Gestión: {e}")
    import traceback
    st.code(traceback.format_exc())
