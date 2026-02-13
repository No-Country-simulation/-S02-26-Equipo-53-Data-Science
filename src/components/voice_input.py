import streamlit as st
from streamlit_mic_recorder import speech_to_text
from src.utils.logger import logInfo, logError

def voice_input_component(key="voice_input", language="es-ES"):
    """
    API de Google Speech Recognition a través de streamlit-mic-recorder.
    
    Args:
        key (str): Clave única para el widget.
        language (str): Código de idioma (default: 'es-ES').
        
    Returns:
        str: El texto reconocido o None.S
    """
    try:
        # Renderizar el botón de micrófono
        text = speech_to_text(
            language=language,
            start_prompt="🎤 Grabar",
            stop_prompt="⏹️ Detener",
            just_once=True,
            use_container_width=True,
            callback=None,
            key=key
        )
        
        if text:
            logInfo(f"Texto reconocido por voz: {text}")
            return text
        return None


            
    except Exception as e:
        logError("Error en componente de voz", e)
        st.error("Error al acceder al micrófono. Asegúrate de estar en HTTPS o localhost.")
        return None
