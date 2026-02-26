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
        Si un campo no se menciona, usa null.
        IMPORTANTE: NO inventes ni extraigas precios, tallas ni colores por separado. Todo el nombre descriptivo debe ir en "producto_dictado".
        
        Campos por objeto:
        - producto_dictado: string (Nombre literal que el usuario dictó, ej: "Polo azul talla M", "Zapatilla Nike")
        - cantidad: integer (default 1)
        - nombre_cliente: string (Nombre del cliente o "Anónimo")
        - ubicacion_cliente: string (Ciudad/Distrito inferido o "Desconocido")
        - genero: string (M/F/U, inferido según el producto o cliente)
        - medio_pago: string (Efectivo, Yape, Plin, Transferencia, Tarjeta, etc. Inferido o "Efectivo")
        - fecha_registro: string (YYYY-MM-DD, hoy es {current_date})

        Ejemplo de salida:
        [
            {{"producto_dictado": "Polo Rojo M", "cantidad": 2, "nombre_cliente": "Juan", "ubicacion_cliente": "Lima", "genero": "M", "medio_pago": "Yape", "fecha_registro": "{current_date}"}}
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
        logError(f"Error en extracción con Gemini: {e}")
        return {"error": str(e), "duration": 0}

def suggest_column_mapping(user_columns: list, required_columns: list) -> dict:
    """
    Usa Gemini para sugerir un emparejamiento entre las columnas del Excel subido 
    y las columnas obligatorias de la tabla destino.
    """
    if not api_key:
        return {}
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Actúa como un ingeniero de datos. Tienes dos listas de nombres de columnas.
        
        Columnas Requeridas en BD: {required_columns}
        Columnas encontradas en el archivo del usuario: {user_columns}
        
        Empareja cada 'Columna Requerida' con la columna del usuario que semánticamente tenga más sentido.
        Si para una Columna Requerida no hay ninguna columna del usuario que encaje, ignórala (no la incluyas en el output).
        
        Devuelve SOLO un JSON donde las CLAVES son los nombres exactos de las "Columnas Requeridas en BD"
        y los VALORES son los nombres exactos de las "Columnas encontradas en el archivo del usuario".
        
        Ejemplo si requieres ["producto", "cantidad"] y el usuario subió ["Articulo_nombre", "cuantos_vendidos", "fecha"]:
        {{"producto": "Articulo_nombre", "cantidad": "cuantos_vendidos"}}
        
        Prohibido usar markdown, solo el JSON puro.
        """
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned_text)
        return {"mapping": getattr(data, 'mapping', data)} # En caso de que devuelva root dict
    except Exception as e:
        logError(f"Error sugiriendo mapeo con Gemini: {e}")
        return {"mapping": {}}

def extract_product_attributes_batch(products: list) -> dict:
    """
    Recibe una lista de descripciones de productos (ej: "Zapatilla Urbana Blanca Talla 40")
    y devuelve una lista de diccionarios con (nombre_limpio, talla, color) inferidos.
    """
    if not api_key or not products:
        return {"data": []}
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Actúa como un experto en catalogación de e-commerce. Recibirás una lista de cadenas de texto 
        que los usuarios escriben para describir productos de ropa o calzado.
        
        Tu tarea es "desempaquetar" cada cadena en 3 atributos:
        1. "producto_base": El nombre limpio del artículo (sin talla ni color). Ej: "Zapatilla Urbana Nike".
        2. "talla": La talla encontrada (texto o número, ej: "S", "M", "L", "XL", "38", "42"). Si no hay, null.
        3. "color": El color predominante (ej: "Blanca", "Negro", "Azul"). Si no hay, null.
        
        Lista de entrada:
        {json.dumps(products, ensure_ascii=False)}
        
        Devuelve una lista JSON con el mismo orden exacto, donde cada objeto tenga:
        {{"original": "cadena original", "producto_base": "...", "talla": "...", "color": "..."}}
        
        SOLO JSON, sin etiquetas markdown.
        """
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned_text)
        return {"data": data}
    except Exception as e:
        logError(f"Error desempaquetando atributos con Gemini: {e}")
        return {"data": []}

