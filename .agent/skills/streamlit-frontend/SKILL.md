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

### 1. Estructura de Layout Premium
- **Sidebar Estratégico:** Usa `st.sidebar` para navegación avanzada mediante `st.navigation` y filtros globales persistentes.
- **Grillas y Contenedores:**
    - Usa `st.columns` para alinear métricas (KPIs) en la parte superior.
    - Agrupa widgets en `st.container` con `key` para aplicar estilos CSS tipo "Card".
- **Jerarquía Visual:** Mantén un orden lógico: Header -> Filtros -> KPIs -> Gráficos Principales -> Tablas de Detalle.

### 2. Estilo y Dinamismo
- **Inyección de CSS Específica:** Utiliza `st.markdown` para inyectar estilos dirigidos por `key`. Ejemplo: estilizar botones específicos (`st-key-[nombre_key]`).
- **Feedback Moderno:**
    - Reemplaza `st.spinner` por `st.status` para pipelines de múltiples pasos.
    - Utiliza `st.toast` para notificaciones discretas que no interrumpan el flujo.
- **Análisis Interactivo:** Integra `PyGWalker` para permitir que el usuario explore datos libremente sin que el desarrollador cree cada gráfico.

### 3. Navegación Avanzada
- Implementa apps multipágina usando `st.Page` y `st.navigation` para separar vistas (Dashboard, Configuración, Carga de Datos).

## Ejemplos
Ver carpeta `examples/` para casos de uso detallados:
- `ejemplo_dashboard_premium.md`: Dashboard con KPIs y Plotly.
- `ejemplo_custom_css.md`: Inyección de estilos avanzados.

## Resources
- `resources/knowledge-source.md`: Base técnica inicial.
- `resources/knowledge-update-2026-02-27.md`: Actualización profesional (Kanaries/SaaS).
- `resources/rules.md`: Reglas de diseño del proyecto.

## Solución de Problemas
- **Parpadeo al actualizar:** Usa `st.empty` para actualizar solo secciones específicas.
- **Gráficos desalineados:** Asegura que `use_container_width=True` esté activo en componentes de visualización.

## Logs
- LOG_INFO: "streamlit-frontend: Renderizando layout de [nombre-pagina]..."
- LOG_SEQUENCE: "Aplicando estilos personalizados a [componente]..."
- LOG_DEBUG: "streamlit-frontend: Actualizando estado de navegación a [página]"
