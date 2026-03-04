import streamlit as st
import sys
import os

# Forzar ruta absoluta al root del proyecto para resolver dependencias
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from modules.ingesta_ventas.app import main

if __name__ == "__main__":
    st.set_page_config(
        page_title="Ingesta de Ventas",
        page_icon="🎙️",
        layout="wide"
    )
    main()
