# Ejemplo: Carga Segura de Excel a PostgreSQL

## Contexto
El usuario tiene un archivo `ventas_semanales.xlsx` que debe subirse a la tabla `public.ventas`.

## Entrada
- Archivo: `ventas_semanales.xlsx`
- Tabla destino: `ventas`

## Proceso

### Script de Procesamiento

```python
import pandas as pd
from sqlalchemy import create_engine, text
import os

# Configuración
DB_URL = os.getenv("DATABASE_URL")
FILE_PATH = "ventas_semanales.xlsx"

def procesar_carga():
    # 1. Conexión
    engine = create_engine(DB_URL)
    
    # 2. Lectura
    print(f"Leyendo {FILE_PATH}...")
    df = pd.read_excel(FILE_PATH)
    
    # 3. Transformación
    # Renombrar columnas para coincidir con DB
    column_mapping = {
        'Fecha Venta': 'fecha',
        'Cliente': 'cliente_id',
        'Total': 'monto'
    }
    df = df.rename(columns=column_mapping)
    
    # Filtrar columnas no deseadas
    valid_columns = ['fecha', 'cliente_id', 'monto']
    df = df[valid_columns]
    
    # 4. Carga con Verificación (Ejemplo Check+Insert)
    with engine.connect() as conn:
        # Obtener IDs existentes para evitar duplicados (si aplica)
        # existing_ids = pd.read_sql("SELECT id FROM ventas", conn)
        
        # Cargar a tabla staging
        df.to_sql('ventas_staging', conn, if_exists='replace', index=False)
        
        # Merge SQL (PostgreSQL example)
        sql_merge = text("""
            INSERT INTO ventas (fecha, cliente_id, monto)
            SELECT fecha, cliente_id, monto FROM ventas_staging
            ON CONFLICT (fecha, cliente_id) DO NOTHING;
        """)
        
        result = conn.execute(sql_merge)
        conn.commit()
        print(f"Insertadas {result.rowcount} filas nuevas.")

if __name__ == "__main__":
    procesar_carga()
```

## Salida Esperada
```
Leyendo ventas_semanales.xlsx...
Insertadas 45 filas nuevas.
```
