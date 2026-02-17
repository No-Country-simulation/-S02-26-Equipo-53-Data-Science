# Ejemplo: Gestión de Estado y Caché

## Contexto
El usuario quiere cargar un dataset de 100MB, procesarlo y permitir su filtrado sin recargar el archivo en cada click.

## Entrada
- Archivo `data.csv`.
- Filtro de categoría.

## Proceso
1. Crear una función decorada con `@st.cache_data` para leer el CSV.
2. Usar `st.session_state` para guardar la selección del usuario.
3. Mostrar los datos filtrados.

## Salida Esperada
```python
import streamlit as st
import pandas as pd

@st.cache_data
def load_data(path):
    # Simula carga pesada
    return pd.read_csv(path)

def main():
    if 'selected_cat' not in st.session_state:
        st.session_state.selected_cat = 'Todas'

    data = load_data('data.csv')
    
    cats = ['Todas'] + list(data['categoria'].unique())
    cat = st.selectbox("Elige categoría", options=cats)
    
    st.session_state.selected_cat = cat
    
    filtered_data = data
    if st.session_state.selected_cat != 'Todas':
        filtered_data = data[data['categoria'] == st.session_state.selected_cat]
        
    st.write(filtered_data)
```
