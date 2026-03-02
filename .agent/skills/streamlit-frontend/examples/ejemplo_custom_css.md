# Ejemplo: Personalización Avanzada con CSS Inyectado

## Contexto
Personalización de la UI de Streamlit más allá de los temas básicos utilizando CSS inyectado para mejorar la estética de botones, contenedores y tipografía.

## Entrada
Una aplicación Streamlit que requiere un look & feel específico de marca o SaaS.

## Proceso
1.  Identificar los elementos a estilizar (usando `inspect element` en el navegador).
2.  Definir un bloque CSS multilínea.
3.  Inyectar el CSS usando `st.markdown` con `unsafe_allow_html=True`.
4.  Usar la `key` del componente para aplicar estilos específicos sin afectar a toda la app.

## Ejemplo de Código
```python
import streamlit as st

# 1. Definición de Estilos
css_custom = """
<style>
    /* Estilo para un contenedor tipo tarjeta */
    [data-testid="stVerticalBlock"] > div:has(div.st-key-premium_card) {
        background-color: #f9f9f9;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #eeeeee;
    }

    /* Botón Premium con Gradiente */
    div.stButton > button.st-key-main_btn {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white !important;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 50px;
        font-weight: bold;
        transition: transform 0.2s ease;
    }

    div.stButton > button.st-key-main_btn:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(110, 142, 251, 0.4);
    }
</style>
"""

st.markdown(css_custom, unsafe_allow_html=True)

# 2. Uso en la Interfaz
with st.container(key="premium_card"):
    st.subheader("Plan Enterprise")
    st.write("Acceso ilimitado a todas las herramientas de IA.")
    if st.button("Suscribirse Ahora", key="main_btn"):
        st.balloons()
```

## Salida Esperada
Un botón con gradiente y efecto hover suave, contenido dentro de un bloque con sombra y bordes redondeados, rompiendo con la estética "plana" por defecto de Streamlit.
