# Ejemplo: Dashboard Premium con KPIs y Análisis

## Contexto
Uso de Streamlit para crear una interfaz de monitoreo profesional con métricas clave y visualización interactiva.

## Entrada
Un dataset de ejemplo (Pandas DataFrame) con métricas de ventas o rendimiento.

## Proceso
1.  Configurar layout horizontal (`st.set_page_config(layout="wide")`).
2.  Definir KPIs principales mediante `st.columns` y `st.metric`.
3.  Cargar y visualizar datos usando gráficos de Plotly o PyGWalker.
4.  Organizar filtros en el `st.sidebar`.

## Ejemplo de Código
```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="SaaS Analytics Dashboard")

# Header
st.title("📊 Panel de Rendimiento SaaS")
st.markdown("---")

# KPIs en la parte superior
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Usuarios Activos", "12,450", "+12%")
with col2:
    st.metric("MRR", "$45,200", "+5.4%")
with col3:
    st.metric("Churn Rate", "2.1%", "-0.5%", delta_color="inverse")
with col4:
    st.metric("NPS", "78", "+2")

st.divider()

# Gráficos Principales
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Tendencia de Ingresos")
    # Simulación de datos
    df_trend = pd.DataFrame({
        'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May'],
        'Ingresos': [10000, 12000, 11500, 14000, 16000]
    })
    fig = px.line(df_trend, x='Mes', y='Ingresos', markers=True)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("Distribución por Plan")
    df_plans = pd.DataFrame({
        'Plan': ['Basic', 'Pro', 'Enterprise'],
        'Count': [200, 150, 45]
    })
    fig_pie = px.pie(df_plans, values='Count', names='Plan', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)
```

## Salida Esperada
Una interfaz limpia, balanceada y visualmente atractiva que permite al usuario entender el estado del negocio de un vistazo.
