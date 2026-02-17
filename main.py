
import streamlit as st

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
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    use_container_width=True
)

st.divider()

# ----------------------
# Seccion "Qué puedes hacer con la app"
# ----------------------
st.header("🚀 Qué puedes hacer con la app")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📁 Subir tus archivos")
    st.write(
        "Carga archivos de ventas, clientes e inventario en Excel."
    )

with col2:
    st.subheader("🧠 Análisis automático")
    st.write(
        "La app detecta columnas, limpia datos y genera métricas clave automáticamente."
    )

with col3:
    st.subheader("📈 Dashboards interactivos")
    st.write(
        "Visualizá KPIs, gráficos y tablas dinámicas listas para usar."
    )

st.divider()

# ----------------------
# Seccion "Cómo funciona"
# ----------------------
st.header("⚙️ Cómo funciona")

step1, step2, step3 = st.columns(3)

with step1:
    st.markdown("### 1️⃣ Carga tus datos")
    st.write("Arrastra uno o varios archivos Excel.")

with step2:
    st.markdown("### 2️⃣ Procesamos la info")
    st.write("Normalizamos y validamos los datos automáticamente.")

with step3:
    st.markdown("### 3️⃣ Explorá los resultados")
    st.write("Dashboards listos para análisis y toma de decisiones.")

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