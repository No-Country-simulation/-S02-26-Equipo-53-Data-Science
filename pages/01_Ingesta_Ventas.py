import streamlit as st
import sys
import os

# Asegurar que podemos importar desde src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.app import main

if __name__ == "__main__":
    st.set_page_config(
        page_title="Ingesta de Ventas",
        page_icon="🎙️",
        layout="centered"
    )
    main()
