# Fuente de Conocimiento: Google Gemini API

**URL Origen**: https://ai.google.dev/gemini-api/docs/get-started/python (Resumido de búsqueda web)
**Fecha Captura**: 2026-02-09

## Resumen del Contenido

### 1. Obtención de API Key
- Se obtiene en Google AI Studio.
- Se recomienda usar variables de entorno (`GOOGLE_API_KEY` o `GEMINI_API_KEY`).

### 2. Instalación
- Paquete Python: `google-generativeai`
- Comando: `pip install -q -U google-generativeai`

### 3. Configuración Básica
```python
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
```

### 4. Inicialización del Modelo
- **Modelos Actuales (Feb 2026)**:
    - `gemini-3-flash`: El estándar actual para velocidad y eficiencia. Reemplaza a 2.5 Flash.
    - `gemini-3-pro`: Modelo más potente para razonamiento complejo.
    - `gemini-2.5-flash`: Versión estable anterior (junio 2025).
- **Deprecados**: `gemini-1.5-flash` (Sep 2025), `gemini-1.5-pro`.

```python
# Usar el modelo más reciente por defecto
model = genai.GenerativeModel('gemini-3-flash')
```

### 5. Generación de Contenido
- Texto a texto:
```python
response = model.generate_content("Escribe un poema sobre la IA")
print(response.text)
```
- Texto multimodal (imágenes):
```python
import PIL.Image
img = PIL.Image.open('imagen.jpg')
response = model.generate_content(["Describe esta imagen", img])
```

### 6. JSON Mode (Salida Estructurada)
- Para obligar al modelo a responder solo JSON, se puede especificar en la configuración de generación o mediante prompt engineering fuerte (como hemos hecho en la app actual).
- En versiones recientes, se soporta `response_mime_type="application/json"` en `generation_config`.
