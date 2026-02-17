# Streamlit Backend Knowledge Source

**Fecha de captura:** 2026-02-08
**Fuentes principales:** Documentation & Community Best Practices

## 1. Gestión de Estado (`st.session_state`)
Streamlit re-ejecuta todo el script ante cada interacción. `st.session_state` permite persistir datos:
- **Persistencia:** Almacena variables que deben sobrevivir a los re-runs (ej. datos de usuario, estados de widgets).
- **Inicialización:** Siempre verificar la existencia de un elemento antes de usarlo: `if 'key' not in st.session_state: st.session_state.key = value`.
- **Callback pattern:** Usar callbacks en widgets para actualizar el estado antes del re-run.

## 2. Estrategias de Caching
- **`@st.cache_data`**: Para funciones de lectura de datos (CSVs, APIs, SQL). Almacena los resultados.
- **`@st.cache_resource`**: Para objetos de conexión (DBs, modelos ML) que deben compartirse entre sesiones.
- **TTL (Time to Live)**: Usar `ttl=3600` para refrescar datos periódicos.

## 3. Optimización de Performance
- **Minimizar Re-runs:** Usar `st.form` para agrupar inputs y procesar una sola vez al hacer click en "Submit".
- **Offloading:** Procesar datos pesados fuera de Streamlit si es posible, o usar procesos en segundo plano.
- **Asincronía:** Streamlit es síncrono por diseño, pero puede manejar `asyncio` con cuidado (ej. peticiones API simultáneas) usando `asyncio.run`.

## 4. Conexiones de Datos
- **Secretos:** Nunca hardcodear credenciales. Usar `.streamlit/secrets.toml`.
- **Seguridad:** Usar consultas parametrizadas para evitar SQL Injection.
- **Thread Safety:** Asegurar que los recursos cacheados sean seguros para hilos (thread-safe).
