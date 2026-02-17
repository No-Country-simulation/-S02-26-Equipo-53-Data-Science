# Reglas: Automatización Tech

1. **Naming:** Los scripts de automatización deben usar `camelCase` para variables y funciones (Ej: `scrapeData`, `priceList`).
2. **Logging:** Es OBLIGATORIO usar `src/utils/logger.js`. Cada paso crítico debe tener un `logSequence`.
3. **Manejo de Errores:** Evita `try-catch` masivos. Prefiere validaciones preventivas antes de realizar acciones (Ej: verificar que el elemento existe antes de hacer click).
4. **No Placeholders:** Si se crea un bot o script, debe ser funcional o requerir solamente la API Key.
5. **Configuración:** Las credenciales deben cargarse desde variables de entorno o un archivo `.env` (nunca hardcoded).
