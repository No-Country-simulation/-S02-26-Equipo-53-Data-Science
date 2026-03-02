# Streamlit Frontend Knowledge Source

**Fecha de captura:** 2026-02-08
**Fuentes principales:** Documentation & Community Best Practices

## 1. UI Layout & Structure
Streamlit ofrece componentes nativos para organizar el contenido:
- **`st.sidebar`**: Navegación y filtros globales.
- **`st.columns`**: Diseño en rejilla (grid) para alinear elementos horizontalmente.
- **`st.expander`**: Ocultar detalles opcionales para limpiar la interfaz.
- **`st.tabs`**: Organizar contenido en pestañas para navegación compacta.
- **`st.container`**: Agrupar elementos lógica o visualmente.
- **`st.empty`**: Placeholder para contenido dinámico o actualizaciones.
- **`st.navigation`**: Para apps multipágina nativas.

## 2. Theming & Estilos
El archivo central de configuración es `.streamlit/config.toml`:
```toml
[theme]
primaryColor="#F63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"
```
- **Custom CSS:** Se puede inyectar CSS global mediante `st.markdown("<style>...</style>", unsafe_allow_html=True)`, aunque se recomienda usar con precaución para evitar romper con actualizaciones futuras.

## 3. Componentes Personalizados
- **Estáticos:** `components.html()` o `components.iframe()` para embeber contenido externo.
- **Bi-direccionales:** Integración con React/Vue para widgets complejos que comunican estado de vuelta a Python.

## 4. Best Practices
- **Diseño Limpio:** Evitar saturación de widgets.
- **Feedback Visual:** Usar `st.spinner`, `st.progress` o `st.toast` para indicar actividad.
- **Consistencia:** Mantener estilos y paleta de colores coherentes.
