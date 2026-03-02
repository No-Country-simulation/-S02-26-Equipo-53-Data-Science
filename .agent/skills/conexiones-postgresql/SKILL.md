---
name: Conexiones PostgreSQL
description: Skill experto en gestión de conexiones a PostgreSQL usando Psycopg 3 (síncrono y asíncrono)
---

# Skill: Conexiones PostgreSQL

## Propósito
Proveer las mejores prácticas, patrones de código y configuraciones seguras para conectar aplicaciones Python a bases de datos PostgreSQL, utilizando la librería moderna `psycopg` (versión 3).

## Cuándo Usar
- Cuando necesites conectar una aplicación Python (script, backend, Streamlit) a PostgreSQL.
- Cuando quieras ejecutar queries SQL de forma segura (parameterized queries).
- Cuando necesites manejar transacciones robustas.
- Cuando requieras alta concurrencia (Connection Pooling o Async).

## Instrucciones y Mejores Prácticas

### 1. Selección del Driver
Usa siempre **Psycopg 3** (paquete `psycopg` o `psycopg[binary]`). Evita `psycopg2` en proyectos nuevos a menos que sea estrictamente necesario por legado.

### 2. Patrón de Conexión Básico (Scripts)
Usa siempre context managers (`with`) para garantizar el cierre de recursos.

```python
import psycopg

# URL de conexión: postgresql://user:password@host:port/dbname
with psycopg.connect("postgresql://usuario:password@localhost:5432/mi_db") as conn:
    with conn.cursor() as cur:
        # Ejecutar comandos
        cur.execute("SELECT 1")
        # El commit es automático al salir del bloque with conn exitosamente
```

### 3. Patrón para Aplicaciones Web (Streamlit/FastAPI)
**NUNCA** abras una conexión nueva por cada recarga o petición. Usa un **Connection Pool**.

```python
from psycopg_pool import ConnectionPool

# Definir el pool una sola vez (ej. en st.cache_resource)
pool = ConnectionPool("postgresql://...")

# Usar una conexión del pool
with pool.connection() as conn:
    conn.execute("...")
```

### 4. Seguridad (SQL Injection)
Jamás concatenes valores en el string SQL. Usa `%s` como placeholder.

- ❌ MAL: `cur.execute(f"SELECT * FROM users WHERE id = {user_id}")`
- ✅ BIEN: `cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))`

### 5. Manejo de Errores
Captura excepciones específicas de `psycopg.Error` para manejo robusto.

```python
try:
    with psycopg.connect(...) as conn:
        ...
except psycopg.OperationalError:
    # Error de conexión (red, auth)
    log_error("No se pudo conectar a la DB")
except psycopg.Error as e:
    # Otros errores de DB
    log_error(f"Error de base de datos: {e}")
```

## Ejemplos
Ver carpeta `examples/` para:
- `ejemplo_basico.md`: Script simple de inserción y consulta.
- `ejemplo_pool.md` (futuro): Uso de Connection Pool.

## Resources
Ver carpeta `resources/` para la fuente de conocimiento original (`knowledge-source.md`).

## Logs
- `LOG_INFO`: "Conexión a PostgreSQL establecida exitosamente"
- `LOG_ERROR`: "Fallo en la conexión a PostgreSQL: [detalle]"
- `LOG_WARN`: "Intento de query sin parámetros detectado (potencial riesgo)"
