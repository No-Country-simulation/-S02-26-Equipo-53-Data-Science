# Ejemplo: Chat Básico con Gemini

## Contexto
Este ejemplo muestra cómo configurar un chat simple con memoria de contexto utilizando `google-generativeai`.

## Entrada
- Un prompt de usuario (texto).
- Historial de chat previo (opcional).

## Proceso
1. Configurar la API Key.
2. Iniciar el modelo `gemini-1.5-flash`.
3. Crear un objeto `chat` con historial vacío.
4. Enviar mensaje y recibir respuesta (stream opcional).

## Código

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Inicializar modelo
model = genai.GenerativeModel('gemini-3-flash')

# Iniciar chat
chat = model.start_chat(history=[])

def send_message(message):
    try:
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Uso
print(send_message("Hola, ¿quién eres?"))
print(send_message("Escribe un resumen de la historia de la IA en 50 palabras."))
```

## Salida Esperada
Texto generado por el modelo respondiendo a las preguntas, manteniendo el contexto de la conversación.
