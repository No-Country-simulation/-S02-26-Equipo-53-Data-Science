import streamlit as st


from libs.logger import logInfo, logSequence, logError
from .services.state_manager import init_staging_state

from .components.voice_input import voice_input_component
from .components.database_viewer import render_db_tab


if __name__ == "__main__":
    st.set_page_config(
        page_title="Hola Mundo Streamlit",
        page_icon="👋",
        layout="centered"
    )

def main():
    # Inicializamos el buffer de staging en memoria al arrancar
    init_staging_state()
    logSequence("Iniciando aplicación", "Hola Mundo")

    st.title("Carga de datos")
    st.write("Selecciona el método de ingreso de ventas:")
    
    # --- Navegación Principal ---
    tab_ia, tab_manual, tab_bulk = st.tabs([
        "🎙️ Dictado IA", 
        "👆 Entrada Manual", 
        "📂 Carga Masiva"
    ])
    
    with tab_ia:
        st.header("Entrada libre por voz y texto")
        render_voice_agent_tab()
    
    with tab_manual:
        from .components.manual_input import render_manual_input_tab
        render_manual_input_tab()
        
    with tab_bulk:
        from .components.mass_upload import render_mass_upload_tab
        render_mass_upload_tab()
        
def render_voice_agent_tab():
    """
    Pestaña de Dictado IA: Delegación completa al componente inteligente.
    """
    if 'sales_data' not in st.session_state:
        st.session_state.sales_data = [] # Inicialización para evitar Error de Atributo
        
    # Pasamos una clave única para el componente en esta pestaña
    voice_input_component(key="voice_main_interface")
    
    st.divider()
    st.info("💡 **Consejo**: Puedes dictar varias ventas seguidas. La IA se encargará de separarlas y validarlas contra el inventario.")

    # La tabla de resultados ya no es necesaria aquí porque se centraliza en el Dashboard del Dueño.
    # El componente voice_input_component ya envía los datos a st.session_state.staging_ventas.
    pass

if __name__ == "__main__":
    main()
