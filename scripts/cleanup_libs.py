
import os
import shutil
import sys
import importlib.util

def cleanup_libs():
    """
    Removes directories in libs/ that are already installed in the current environment.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    libs_dir = os.path.join(project_root, "libs")
    
    print(f"Propósito: Limpiar librerías redundantes en {libs_dir}")
    print(f"Python actual: {sys.executable}")
    
    if not os.path.exists(libs_dir):
        print(f"Directorios libs no encontrado: {libs_dir}")
        return

    # Lista de carpetas/archivos a ignorar (NUNCA borrar)
    KEEP_SAFE = ["db_connection.py", "logger.py", "styles", "__pycache__", ".gitkeep"]

    # Obtener lista de items en libs
    items = os.listdir(libs_dir)
    
    for item in items:
        if item in KEEP_SAFE:
            continue
            
        item_path = os.path.join(libs_dir, item)
        
        # Determinar nombre del paquete (asumiendo que nombre carpeta = nombre paquete)
        # Ojo: psycopg2 en carpeta se llama 'psycopg2', en pip también.
        # numpy.libs -> ignorar o borrar si numpy se borra? Mejor borrar si es carpeta y parece lib.
        
        package_name = item.split("-")[0].split(".")[0] # simple heuristic
        
        # Intentar importar
        try:
            # Check if installed in environment (not local libs)
            # We use importlib to check if it's resolvable
            if package_name in sys.modules:
                 # Already loaded?
                 pass
            
            spec = importlib.util.find_spec(package_name)
            if spec and spec.origin:
                # Si el origen NO está en libs, entonces está en site-packages (o global)
                if "libs" not in spec.origin:
                    print(f"✅ {item} está instalado en entorno ({spec.origin}). BORRANDO de libs...")
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                else:
                    print(f"ℹ️ {item} solo existe en libs. Se mantiene.")
            else:
                # Si no se puede importar, tal vez es basura o una lib necesaria.
                # Para seguridad, si es una carpeta 'trash' conocida (como .dist-info de libs copiadas) borrar.
                if item.endswith(".dist-info") or item.endswith(".libs"):
                     print(f"🗑️ Borrando metadatos/artefacto: {item}")
                     if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                else:
                    print(f"⚠️ No se detectó instalación de {item}. Se mantiene.")
                    
        except Exception as e:
            print(f"Error procesando {item}: {e}")

if __name__ == "__main__":
    cleanup_libs()
