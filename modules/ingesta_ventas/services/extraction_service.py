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
        model = genai.GenerativeModel('gemini-2.5-flash')
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        prompt = f"""
        Actúa como un asistente de ventas experto. Tu tarea es extraer información estructurada de este texto de voz que puede contener UNA O MÁS ventas:
        "{text_input}"
        
        Debes devolver una LISTA JSON de objetos. Cada objeto representa una venta.
        
        REGLAS CRÍTICAS:
        1. producto_base: Extrae SOLO el nombre base del artículo (ej: si dice "Polo azul talla M", producto_base es "Polo").
        2. talla/color: Extrae estos atributos por separado. Si no se mencionan, usa null.
        3. Si un campo no se menciona EXPLÍCITAMENTE, usa null. NO INVENTES DATOS.
        4. medio_pago: Solo extrae si el usuario dice algo como "pagó con yape", "en efectivo", etc.
        
        Campos por objeto:
        - producto_base: string (Nombre del artículo)
        - talla: string/number o null
        - color: string o null
        - cantidad: integer (default 1)
        - precio: number o null
        - nombre_cliente: string o null
        - ubicacion_cliente: string o null
        - genero: string o null (M/F/U)
        - medio_pago: string o null
        - fecha_registro: string (YYYY-MM-DD, hoy es {current_date})

        Responde SOLO con la LISTA JSON. Sin bloques de código markdown.
        """
        
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned_text)
        
        if isinstance(data, dict):
            data = [data]
            
        return {"data": data, "duration": (datetime.datetime.now() - start_time).total_seconds()}

    except Exception as e:
        logError(f"Error en extracción con Gemini: {e}")
        return {"error": str(e), "duration": 0}

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

def detect_business_antipatterns(sales_df_json: str):
    """
    Usa Gemini para auditar un listado de ventas en staging y detectar anomalías de negocio.
    """
    if not api_key:
        return {"warnings": []}
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Actúa como un Auditor de Negocios y Experto en Control de Pérdidas.
        Analiza este listado de ventas (en formato JSON) que están a punto de registrarse:
        
        "{sales_df_json}"
        
        Tu objetivo es detectar "Antipatrones de Negocio" o anomalías. Ejemplos:
        - Ventas con precio 0 o excesivamente bajo/alto comparado con otros items similares.
        - Cantidades inusualmente grandes para un solo cliente.
        - Mismo cliente comprando el mismo item varias veces en segundos (posible duplicidad).
        - Advertencias sobre clientes "Anónimos" recurrentes que deberían ser registrados.
        
        Para cada anomalía encontrada, devuelve un objeto JSON con:
        1. "gravedad": "Alta", "Media" o "Baja".
        2. "mensaje": Una explicación breve de qué está mal.
        3. "consecuencia": Qué impacto tiene esto para el dueño (ej: "Pérdida de margen", "Error de inventario").
        
        Responde SOLO con una LISTA JSON de estos objetos. Si no hay anomalías, devuelve una lista vacía [].
        """
        
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        warnings = json.loads(cleaned_text)
        return {"warnings": warnings}
    except Exception as e:
        logError(f"Error en auditoría IA: {e}")
        return {"warnings": [{"gravedad": "Baja", "mensaje": "No se pudo completar la auditoría IA.", "consecuencia": "Revisión manual requerida."}]}

