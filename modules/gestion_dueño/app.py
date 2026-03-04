import streamlit as st
import sys
import os

# Calculamos la raíz del proyecto de forma absoluta (sin '..') para evitar KeyError en Streamlit Cloud
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modules.gestion_dueño.components.dashboard_main import render_owner_dashboard

def main():
    """
    Punto de entrada para el módulo de Gestión del Dueño.
    """
    render_owner_dashboard()

if __name__ == "__main__":
    main()
