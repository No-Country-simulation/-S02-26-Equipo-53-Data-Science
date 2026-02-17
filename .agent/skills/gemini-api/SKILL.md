---
name: Integración Gemini API
description: Skill para integrar y utilizar la API de Google Gemini en proyectos Python
---

# Skill: Integración Gemini API

## Propósito
Facilitar la integración de capacidades de IA generativa utilizando la API de Google Gemini (modelos Flash, Pro, etc.) en aplicaciones Python. Este skill proporciona patrones probados para configuración, generación de texto, manejo de multimodalidad y respuestas estructuradas (JSON).

## Cuándo Usar
- Cuando se requiera procesar lenguaje natural (resumen, extracción, chat).
- Cuando se necesite visión artificial (describir imágenes, extraer texto de fotos).
- Cuando se busque una alternativa eficiente y económica a otros LLMs.

## Instrucciones

### 1. Prerrequisitos
- Tener una API Key válida de Google AI Studio.
- Tener la variable de entorno `GEMINI_API_KEY` configurada en `.env`.

### 2. Instalación
```bash
pip install -q -U google-generativeai
```

### 3. Patrón de Uso Básico
```python
import google.generativeai as genai
import os

# Configuración
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Inicialización (Usar 'gemini-3-flash' por defecto para eficiencia)
model = genai.GenerativeModel('gemini-3-flash')

# Generación
response = model.generate_content("Tu prompt aquí")
print(response.text)
```

### 4. Mejores Prácticas
- **Manejo de Errores**: Envolver las llamadas en try-except para manejar cuotas excedidas o errores de red.
- **Configuración de Seguridad**: Ajustar los `safety_settings` si el contenido puede ser sensible.
- **JSON Mode**: Para obtener datos estructurados, ser explícito en el prompt o usar la configuración de generación adecuada.

## Ejemplos
Ver carpeta `examples/` para casos de uso específicos como extracción de datos o chat.

## Resources
Ver carpeta `resources/` para documentación de referencia.

## Logs
- LOG_INFO: "gemini-api: Inicializando modelo [modelo]..."
- LOG_INFO: "gemini-api: Generando contenido para [prompt_corto]..."
- LOG_ERROR: "gemini-api: Error en generación: [error]"
