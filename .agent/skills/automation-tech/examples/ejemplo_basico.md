# Ejemplo: Planificación de Automatización Web

## Contexto
El usuario quiere automatizar la extracción de precios de un sitio e-commerce diariamente.

## Entrada
- URL del sitio.
- Lista de productos.
- Frecuencia: Diaria.

## Proceso (Ejecutado por el Skill)
1. **Validación:** Analizar si el sitio es estático o requiere JS.
2. **Selección de Herramienta:** Seleccionar `Playwright` (si es dinámico) o `BeautifulSoup`.
3. **Diseño del Flujo:**
   - Cargar URLs.
   - Extraer campos (título, precio).
   - Guardar en CSV/Pandas.
4. **Logs:** Implementar `logSequence` para cada paso de la extracción.

## Salida Esperada
Un script de Python que utiliza la herramienta seleccionada, sigue las convenciones de naming del proyecto (`camelCase`) e incluye el sistema de logging obligatorio.
