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

# Lista de modelos por orden de preferencia (Fallback)
MODELS_BACKUP = [
    "gemini-3.1-flash-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-1.5-flash" # El más estable
]

def _generate_with_fallback(prompt: str):
    """
    Intenta generar contenido con una lista de modelos hasta que uno funcione.
    """
    last_error = ""
    for model_name in MODELS_BACKUP:
        try:
            logInfo(f"Intentando generación con modelo: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            # Limpieza robusta de la respuesta
            text = response.text.strip()
            # Eliminar bloques de código markdown si existen
            if "```" in text:
                # Extraer contenido entre las primeras y últimas comillas triples
                parts = text.split("```")
                for p in parts:
                    p_clean = p.strip()
                    if p_clean.startswith("json"): p_clean = p_clean[4:].strip()
                    if p_clean.startswith("[") or p_clean.startswith("{"):
                        text = p_clean
                        break
            
            # Validar que sea JSON parseable
            data = json.loads(text)
            return data, model_name
        except Exception as e:
            last_error = str(e)
            logError(f"Fallo con modelo {model_name}: {e}")
            continue
            
    raise Exception(f"Todos los modelos fallaron. Último error: {last_error}")

def extract_sales_data(text_input: str):
    """
    Extrae datos estructurados de ventas a partir de texto libre usando multi-modelo fallback.
    """
    if not api_key:
        return {"error": "API Key no configurada"}
        
    try:
        start_time = datetime.datetime.now()
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        prompt = f"""
        Actúa como un asistente de ventas experto. Extrae información estructurada de este texto:
        "{text_input}"
        
        Devuelve una LISTA JSON de objetos. 
        REGLAS:
        1. producto_base: Solo nombre base (ej: "Polo").
        2. talla/color: Por separado o null.
        3. SI NO SE DICE EXPLICITAMENTE, USA null. NO INVENTES.
        
        Campos: producto_base, talla, color, cantidad, precio, nombre_cliente, ubicacion_cliente, genero, medio_pago, fecha_registro (hoy es {current_date}).
        
        Responde SOLO con la LISTA JSON. Sin bloques de markdown.
        """
        
        data, used_model = _generate_with_fallback(prompt)
        
        if isinstance(data, dict):
            data = [data]
            
        return {
            "data": data, 
            "model": used_model,
            "duration": (datetime.datetime.now() - start_time).total_seconds()
        }

    except Exception as e:
        logError(f"Error total en extracción: {e}")
        return {"error": str(e), "duration": 0}

def suggest_column_mapping(user_columns: list, required_columns: list) -> dict:
    """
    Sugerencia de mapeo con fallback.
    """
    if not api_key:
        return {}
        
    try:
        prompt = f"""
        Empareja Columnas Requeridas {required_columns} con Columnas Usuario {user_columns}.
        Devuelve SOLO JSON {{ "req": "user" }}.
        """
        data, _ = _generate_with_fallback(prompt)
        return {"mapping": data}
    except Exception as e:
        logError(f"Error en mapeo IA: {e}")
        return {"mapping": {}}

def extract_product_attributes_batch(products: list) -> dict:
    """
    Desempaqueta atributos en lote con fallback.
    """
    if not api_key or not products:
        return {"data": []}
        
    try:
        prompt = f"""
        Desempaqueta esta lista de productos en producto_base, talla y color:
        {json.dumps(products, ensure_ascii=False)}
        Devuelve lista JSON de objetos con "original", "producto_base", "talla", "color".
        """
        data, _ = _generate_with_fallback(prompt)
        return {"data": data}
    except Exception as e:
        logError(f"Error en desempaque lote IA: {e}")
        return {"data": []}

def detect_business_antipatterns(sales_df_json: str):
    """
    Auditoría de negocio con fallback.
    """
    if not api_key:
        return {"warnings": []}
        
    try:
        prompt = f"""
        Audita este JSON de ventas y detecta anomalías (precios raros, duplicados, etc):
        "{sales_df_json}"
        Devuelve lista JSON con "gravedad", "mensaje", "consecuencia".
        """
        warnings, _ = _generate_with_fallback(prompt)
        return {"warnings": warnings}
    except Exception as e:
        logError(f"Error en auditoría IA: {e}")
        return {"warnings": []}

def classify_products_categories_batch(product_names: list) -> dict:
    """
    Clasifica una lista de nombres de productos en categorías permitidas.
    """
    if not api_key or not product_names:
        return {"data": {}}
        
    try:
        prompt = f"""
        Clasifica esta lista de nombres de productos en estrictamente UNA de estas tres categorías: "Ropa", "Calzado" o "Accesorio".
        {json.dumps(product_names, ensure_ascii=False)}
        Devuelve SOLO un DICCIONARIO JSON donde la clave sea el nombre del producto exacto y el valor sea la categoría asignada.
        Ejemplo: {{"Zapatilla Nike": "Calzado", "Polo Rojo": "Ropa", "Reloj Casio": "Accesorio"}}
        No uses markdown, solo el diccionario JSON crudo.
        """
        data, _ = _generate_with_fallback(prompt)
        return {"data": data}
    except Exception as e:
        logError(f"Error en clasificación de categorías por IA: {e}")
        return {"data": {}}

