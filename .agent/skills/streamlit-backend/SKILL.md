---
name: Streamlit Backend
description: Experto en gestión de estado, caching, performance y conexiones de datos en Streamlit
---

# Skill: Streamlit Backend

## Propósito
Optimizar el rendimiento y la robustez lógica de aplicaciones Streamlit mediante el uso avanzado de caching, gestión de sesiones y conexiones seguras a datos.

## Cuándo Usar
- Al implementar lógica que requiera persistencia entre interacciones del usuario.
- Al conectar la aplicación a bases de datos, APIs o archivos pesados.
- Al optimizar tiempos de carga mediante estrategias de caché.
- Al manejar secretos y configuraciones sensibles.

## Instrucciones

### 1. Gestión de Estado Eficiente
- Inicializa siempre los valores en `st.session_state` al inicio del script o en una función `init()`.
- Usa el parámetro `key` en widgets para vincularlos directamente al estado.

### 2. Implementación de Caché
- Usa `@st.cache_data` para transformaciones de datos y lecturas de archivos.
- Usa `@st.cache_resource` para carguer de modelos o conexiones a DB.
- **Recuerda:** Las funciones cacheadas deben ser puras (mismos inputs = mismo output).

### 3. Conexiones Seguras
- Almacena credenciales en `.streamlit/secrets.toml` y accede vía `st.secrets`.
- Cierra siempre las conexiones a bases de datos o usa gestores de contexto (`with`).

### 4. Control de Re-ejecución
- Usa `st.form` cuando el usuario deba completar múltiples campos antes de ver un resultado.
- Aprovecha `st.fragment` (si está disponible en la versión) para re-renderizar solo partes específicas de la UI.

## Ejemplos
Ver carpeta `examples/` para patrones de caché y estado.

## Resources
- `resources/knowledge-source.md`: Guía técnica de caching y performance.
- `resources/rules.md`: Reglas de lógica y seguridad backend.

## Logs
- LOG_INFO: "streamlit-backend: Cargando datos desde [fuente]..."
- LOG_SEQUENCE: "Actualizando st.session_state con nuevos valores de [feature]..."
- LOG_WARN: "Caché invalidada para [función] debido a [razón]..."
