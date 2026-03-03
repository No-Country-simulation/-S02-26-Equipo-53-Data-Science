import streamlit as st
import sys
import os

# Asegurar que el path incluya la raíz para imports absolutos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.gestion_dueño.components.dashboard_main import render_owner_dashboard

def main():
    """
    Punto de entrada para el módulo de Gestión del Dueño.
    """
    render_owner_dashboard()

if __name__ == "__main__":
    main()
