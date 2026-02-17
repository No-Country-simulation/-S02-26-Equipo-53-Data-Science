---
name: Streamlit Frontend
description: Experto en diseño de interfaces, layouts y componentes visuales en Streamlit
---

# Skill: Streamlit Frontend

## Propósito
Optimizar la experiencia de usuario (UX) y el diseño visual (UI) de aplicaciones Streamlit, utilizando componentes de layout nativos y personalización avanzada.

## Cuándo Usar
- Al diseñar la estructura principal de una aplicación.
- Al organizar widgets para mejorar la legibilidad.
- Al personalizar colores, fuentes y estilos mediante configuración o CSS.
- Al implementar navegación en aplicaciones multipágina.

## Instrucciones

### 1. Estructura de Layout Profesional
- **Sidebar para Globales:** Usa `st.sidebar` para filtros que afecten a toda la página o para la navegación principal.
- **Grillas Dinámicas:** Utiliza `st.columns` para alinear métricas o widgets pequeños. Evita más de 3-4 columnas en pantallas estándar.
- **Jerarquía Visual:** Usa encabezados (`st.header`, `st.subheader`) y divisores (`st.divider`) para separar secciones lógicas.
- **Contención:** Agrupa elementos relacionados en `st.container` o `st.expander` para mantener la interfaz limpia.

### 2. Estilo y Temas
- **Configuración:** Prioriza el uso de `.streamlit/config.toml` para cambios globales de tema.
- **Custom CSS:** Solo cuando sea estrictamente necesario, inyecta estilos usando:
  ```python
  st.markdown("<style>...</style>", unsafe_allow_html=True)
  ```

### 3. Feedback al Usuario
- Indica carga de datos pesados con `st.spinner("Cargando...")`.
- Notifica éxitos o errores con `st.toast` o `st.success`/`st.error`.

## Ejemplos
Ver carpeta `examples/` para patrones de diseño comunes.

## Resources
- `resources/knowledge-source.md`: Documentación detallada de componentes visuales.
- `resources/rules.md`: Reglas de diseño para el proyecto.

## Logs
- LOG_INFO: "streamlit-frontend: Renderizando layout de [nombre-pagina]..."
- LOG_SEQUENCE: "Aplicando estilos personalizados a [componente]..."
