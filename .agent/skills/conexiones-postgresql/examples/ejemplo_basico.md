# Ejemplo: Conexión Básica y Operaciones CRUD en PostgreSQL

## Contexto
Este ejemplo muestra cómo crear un script simple que se conecta a una base de datos PostgreSQL, crea una tabla si no existe, inserta datos de forma segura y realiza una consulta. Es ideal para scripts de migración, tareas cron o utilidades CLI.

## Entrada
- Cadena de conexión a PostgreSQL (Connection String).
- Datos a insertar.

## Proceso

1. Establecer conexión usando `psycopg.connect`.
2. Crear un cursor.
3. Ejecutar DDL (Create Table).
4. Ejecutar DML (Insert) con parámetros.
5. Ejecutar Select y mostrar resultados.
6. Commit automático al cerrar el bloque `with`.

## Código de Ejemplo

```python
import psycopg
import os
from datetime import datetime

# Se recomienda usar variables de entorno para credenciales
DB_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test_db")

def main():
    print(f"Conectando a {DB_URI}...")
    
    try:
        # El bloque 'with' maneja la conexión y el commit/rollback
        with psycopg.connect(DB_URI) as conn:
            
            # El bloque 'with' para el cursor maneja su cierre
            with conn.cursor() as cur:
                
                # 1. Crear Tabla
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        id SERIAL PRIMARY KEY,
                        mensaje TEXT NOT NULL,
                        creado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("Tabla 'logs' verificada.")

                # 2. Insertar Dato (Parametrizado)
                mensaje_usuario = "Prueba de conexión exitosa"
                cur.execute(
                    "INSERT INTO logs (mensaje) VALUES (%s) RETURNING id",
                    (mensaje_usuario,)
                )
                
                # Obtener el ID generado
                nuevo_id = cur.fetchone()[0]
                print(f"Log insertado con ID: {nuevo_id}")

                # 3. Consultar Datos
                cur.execute("SELECT id, mensaje, creado_em FROM logs ORDER BY id DESC LIMIT 5")
                
                rows = cur.fetchall()
                print("\n--- Últimos Logs ---")
                for row in rows:
                    print(f"[{row[0]}] {row[2]}: {row[1]}")
        
        # Al salir del bloque con éxito, se hace commit automático
        print("\nOperación completada exitosamente.")

    except psycopg.OperationalError as e:
        print(f"Error de conexión: {e}")
        # Aquí podrías implementar lógica de reintento
    except psycopg.Error as e:
        print(f"Error de base de datos: {e}")

if __name__ == "__main__":
    main()
```

## Salida Esperada

```text
Conectando a postgresql://...
Tabla 'logs' verificada.
Log insertado con ID: 1

--- Últimos Logs ---
[1] 2026-02-13 10:00:00: Prueba de conexión exitosa
Operación completada exitosamente.
```
