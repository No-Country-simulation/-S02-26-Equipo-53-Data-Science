import streamlit as st

from modules.gestion_dueño.components.dashboard_main import render_owner_dashboard

def main():
    """
    Punto de entrada para el módulo de Gestión del Dueño.
    """
    render_owner_dashboard()

if __name__ == "__main__":
    main()
