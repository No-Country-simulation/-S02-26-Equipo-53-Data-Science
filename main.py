import streamlit as st
import sys
import os

# Add libs to sys.path to support local dependencies (psycopg2, pandas, etc.)
libs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

# ----------------------
# config
# ----------------------
st.set_page_config(
    page_title="DATAMARK ",
    page_icon="📊",
    layout="wide"
)

# ----------------------
# Hero 
# ----------------------
st.title("📊 Plataforma de Data Analyst Automatizado")
st.subheader("Convierte archivos de Excel en dashboards interactivos en segundos")

st.write(
    """
    Una plataforma pensada para pequeños negocios de ropa y calzado en provincias del Perú que quieren **analizar, visualizar
    y tomar decisiones** sin uso de herramientas complejas.
    """
)

st.image(
    "imagen/Portada-Plataforma.png",
    use_container_width=True
)

st.divider()

# ----------------------
# Seccion "Qué puedes hacer con la app"
# ----------------------
st.header("🚀 Qué puedes hacer con la app")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🎙️ Ingesta Inteligente")
    st.write(
        "Registra ventas con tu voz o carga Excels sueltos. La Inteligencia Artificial extrae, autocompleta precios y deduce categorías."
    )

with col2:
    st.subheader("🧠 Integridad Automática")
    st.write(
        "Verifica colisiones de stock y limpia valores inválidos matemáticamente para proteger tu operativa de cuelgues del sistema."
    )

with col3:
    st.subheader("📈 Dashboards y Base de Datos")
    st.write(
        "Navega por tus registros tabulares, edítalos dinámicamente o disfruta de visualizaciones consolidadas de tu negocio vivo."
    )

st.divider()

# ----------------------
# Seccion "Cómo funciona"
# ----------------------
st.header("⚙️ Cómo funciona")

step1, step2, step3 = st.columns(3)

with step1:
    st.markdown("### 1️⃣ Carga Cero Fricción")
    st.write("Usa comandos de voz en tienda, o arrastra tus Excel históricos.")

with step2:
    st.markdown("### 2️⃣ Cruce Relacional IA")
    st.write("Gemini Flash mapea campos ignorados cruzándolos con tu BD.")

with step3:
    st.markdown("### 3️⃣ Control Total")
    st.write("Un panel interactivo para revisar, corregir o inyectar las ventas.")

st.divider()

# ----------------------
# Boton de accion 
# ----------------------
st.header("✨ Empieza ahora")

st.write(
    "Conecta tus  datos y empieza a analizar en minutos."
)



if st.button("🚀 Ir a la carga de datos"):
    st.switch_page("pages/01_Ingesta_Ventas.py")



# ----------------------
# Footer
# ----------------------
st.divider()
st.caption("© 2026 Plataforma de Data Analyst Automatizado · DATAMARK")