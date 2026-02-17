# Fuente de Conocimiento: Conexiones PostgreSQL con Psycopg 3

**Origen:** Documentación Oficial Psycopg 3 (psycopg.org) y guías de mejores prácticas.
**Fecha:** 2026-02-13

## Resumen Ejecutivo

Psycopg 3 es el adaptador de base de datos PostgreSQL más moderno y recomendado para Python. Difiere significativamente de Psycopg 2 en su soporte nativo para `asyncio`, uso de parámetros del lado del servidor (fijados), y una gestión de conexiones más robusta.

## Puntos Clave

### 1. Instalación
```bash
pip install "psycopg[binary]"
```
Se recomienda la versión binaria para desarrollo y despliegue estándar.

### 2. Uso de Context Managers
Psycopg 3 está diseñado para ser usado con bloques `with`. Esto asegura que las conexiones y cursores se cierren correctamente, incluso si ocurren errores.

```python
import psycopg

with psycopg.connect("dbname=test user=postgres") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM table")
```

### 3. Parámetros y Seguridad
NUNCA concatenar strings. Usar siempre el paso de parámetros, que Psycopg gestiona de forma segura.

**Incorrecto:**
```python
cur.execute("INSERT INTO numbers VALUES (" + str(num) + ")")
```

**Correcto:**
```python
cur.execute("INSERT INTO numbers VALUES (%s)", (num,))
```

### 4. Transacciones
En Psycopg 3, la transacción está implícita en el bloque `with` de la conexión si no está en modo autocommit. Sin embargo, es mejor práctica usar `conn.transaction()` para bloques transaccionales explícitos o métodos helper.
Por defecto, Psycopg 3 abre una transacción. Al salir del bloque `with conn:`, si no hubo excepción, hace commit. Si hubo excepción, hace rollback.

### 5. Connection Pools (Crítico para WebApps)
Para aplicaciones como Streamlit o FastAPI, **no** crear una conexión por request. Usar `psycopg_pool.ConnectionPool`.

```python
from psycopg_pool import ConnectionPool

with ConnectionPool("conn_string") as pool:
    with pool.connection() as conn:
        conn.execute("...")
```

### 6. Soporte Async
Para aplicaciones asíncronas (FastAPI, integraciones async), usar `AsyncConnection`.

```python
async with await psycopg.AsyncConnection.connect("...") as aconn:
    async with aconn.cursor() as acur:
        await acur.execute("...")
```

## Diferencias con Psycopg 2
- Soporte nativo de `asyncio`.
- Preparación de queries del lado del servidor por defecto.
- API más limpia y tipada.
