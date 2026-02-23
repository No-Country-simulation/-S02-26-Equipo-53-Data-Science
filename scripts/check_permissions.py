
import sys
import os

# Explicitly add the libs directory using absolute path
libs_path = r"e:\OSCAR\HACKATONES\data-science-grupo-26\libs"
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

import psycopg2
from dotenv import load_dotenv

# Re-load env manually to be sure
load_dotenv()

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
schema = os.getenv("DB_SCHEMA", "raw")

print(f"--- DIAGNOSTICO DE CONEXIÓN ---")
print(f"Intentando conectar como usuario: '{user}'")
print(f"Base de datos: '{database}' en '{host}'")
print(f"Schema objetivo: '{schema}'")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    print("✅ Conexión EXITOSA.")
    
    with conn.cursor() as cursor:
        # 1. Verificar usuario actual
        cursor.execute("SELECT current_user;")
        current_user = cursor.fetchone()[0]
        print(f"ℹ️  Usuario en sesión: '{current_user}'")

        # 2. Verificar permisos
        print(f"\n--- INTENTO DE INSERT EN {schema}.ventas_raw ---")
        try:
            # Intentamos insertar un registro dummy que falle por constraint o NULL,
            # pero que al menos pase la barrera de permisos.
            # Usamos NULLs para casi todo para ver si el error es de PERMISO o de DATOS.
            query = f"""
                INSERT INTO {schema}.ventas_raw (fecha, cantidad, precio_venta_unitario)
                VALUES (NOW(), 1, 1.0)
                RETURNING id_venta
            """
            print(f"Ejecutando: {query.strip()}")
            cursor.execute(query)
            new_id = cursor.fetchone()[0]
            print(f"✅ ¡INSERT EXITOSO! ID generado: {new_id}")
            conn.rollback() # Deshacer para no ensuciar
            print("ℹ️  Rollback realizado (prueba exitosa)")
            
        except psycopg2.errors.InsufficientPrivilege as e:
            print(f"\n❌ ERROR DE PERMISOS CONFIRMADO:")
            print(f"   {e}")
            print(f"\nCONCLUSIÓN: El usuario '{user}' NO tiene permisos de escritura en la tabla.")
            
        except Exception as e:
            print(f"\n❌ OTRO ERROR AL INSERTAR:")
            print(f"   {e}")
            
    conn.close()

except Exception as e:
    print(f"❌ Error fatal de conexión: {e}")
