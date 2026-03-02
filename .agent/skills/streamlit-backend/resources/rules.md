# Reglas: Streamlit Backend

1. **Eficiencia en Caché:** No caches funciones que dependan de variables globales que cambian fuera de la función; usa inputs explícitos.
2. **Secretos:** Queda prohibido escribir credenciales en archivos `.py`. Usa siempre el sistema de secretos de Streamlit.
3. **Optimización de Memoria:** No almacenes objetos gigantes en `st.session_state` si pueden ser regenerados rápidamente o leídos de caché.
4. **Validación de Datos:** Siempre valida los inputs del usuario antes de pasarlos a funciones de procesamiento o consultas SQL.
5. **Logs de Lógica:** Usa `logInfo` para trazar el flujo de carga de datos y `logError` para fallos de conexión.
