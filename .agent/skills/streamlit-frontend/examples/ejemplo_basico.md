# Ejemplo: Layout de Dashboard Profesional

## Contexto
El usuario quiere una página principal con una barra lateral de filtros y una cuadrícula de métricas en el centro.

## Entrada
- Métricas: Ventas, Usuarios, Ratio.
- Filtros: Fecha, Región.

## Proceso
1. Configurar la página con `st.set_page_config`.
2. Crear filtros en la barra lateral usando `st.sidebar`.
3. Crear una fila de métricas usando `st.columns`.
4. Mostrar un gráfico principal debajo.

## Salida Esperada
```python
import streamlit as st

def main():
    st.set_page_config(page_title="Dashboard Ventas", layout="wide")
    
    # Sidebar
    st.sidebar.title("Configuración")
    date_range = st.sidebar.date_input("Rango de fechas")
    
    # Header
    st.title("🚀 Panel de Control")
    st.divider()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Total", "$12,450", "+12%")
    col2.metric("Usuarios Activos", "1,200", "-5%")
    col3.metric("Conversión", "3.2%", "+0.5%")
    
    st.subheader("Tendencia de Ventas")
    # ... código del gráfico
```
