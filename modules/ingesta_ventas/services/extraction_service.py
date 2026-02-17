import os
import json
import google.generativeai as genai
from libs.logger import logError, logInfo
from dotenv import load_dotenv
import datetime

# Cargar variables de entorno
load_dotenv()

# Configurar API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logError("GEMINI_API_KEY no encontrada en variables de entorno.")
else:
    genai.configure(api_key=api_key)

def extract_sales_data(text_input: str):
    """
    Extrae datos estructurados de ventas a partir de texto libre usando Gemini Flash.
    """
    if not api_key:
        return {"error": "API Key no configurada"}
        
    try:
        start_time = datetime.datetime.now()
        # Usar modelo estable disponible
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        prompt = f"""
        Actúa como un asistente de ventas experto. Tu tarea es extraer información estructurada de este texto de voz que puede contener UNA O MÁS ventas:
        "{text_input}"
        
        Debes devolver una LISTA JSON de objetos. Cada objeto representa una venta.
        Si un campo no se menciona, usa null (o estimaciones lógicas basadas en el contexto).
        
        Campos por objeto:
        - producto: string (Nombre del producto vendido)
        - categoria: string (Categoría inferida, ej: Ropa, Tecnología, Alimentos, etc.)
        - cantidad: integer (default 1)
        - talla: string (S, M, L, o números como 38, 42, 38.5, null si no aplica)
        - color: string (null si no aplica)
        - precio: float (0.0 si no se dice)
        - nombre_cliente: string (Nombre del cliente o "Anónimo")
        - ubicacion_cliente: string (Ciudad/Distrito inferido o "Desconocido")
        - genero: string (M/F/U, inferido según el producto o cliente)
        - medio_pago: string (Efectivo, Yape, Plin, Transferencia, Tarjeta, etc. Inferido o "Efectivo")
        - fecha_registro: string (YYYY-MM-DD, hoy es {current_date})

        Ejemplo de salida:
        [
            {{"producto": "Polo Rojo", "categoria": "Ropa", "cantidad": 2, "talla": "M", "color": "Rojo", "precio": 50.0, "nombre_cliente": "Juan", "ubicacion_cliente": "Lima", "genero": "M", "medio_pago": "Yape", "fecha_registro": "{current_date}"}},
            {{"producto": "Laptop", "categoria": "Tecnología", "cantidad": 1, "talla": null, "color": "Gris", "precio": 1500.0, "nombre_cliente": "Maria", "ubicacion_cliente": "Arequipa", "genero": "F", "medio_pago": "Tarjeta", "fecha_registro": "{current_date}"}}
        ]

        Responde SOLO con la LISTA JSON. Sin bloques de código markdown.
        """
        
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        
        data = json.loads(cleaned_text)
        
        # Asegurar que sea una lista
        if isinstance(data, dict):
            data = [data]
            
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logInfo(f"Datos extraídos en {duration:.2f}s: {len(data)} registros")
        return {"data": data, "duration": duration}

    except Exception as e:
        logError("Error en extracción con Gemini", e)
        return {"error": str(e), "duration": 0}
