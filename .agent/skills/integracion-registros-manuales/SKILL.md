---
name: Integración Registros Manuales
description: Estandarización y carga de datos manuales (Excel/CSV) a bases de datos generales
---

# Skill: Integración de Registros Manuales

## Propósito
Proveer un flujo de trabajo estandarizado y seguro para incorporar datos generados manualmente (hojas de cálculo, CSVs) a la base de datos central del proyecto, asegurando integridad, consistencia y trazabilidad.

## Cuándo Usar
- Cuando el usuario tiene archivos Excel/CSV con datos nuevos.
- Cuando se necesita actualizar catálogos o tablas maestras manualmente.
- Cuando se requiere reconciliar datos de diferentes fuentes manuales.
- Al detectar inconsistencias entre reportes manuales y el sistema central.

## Instrucciones

### 1. Validación de Fuente
- Verificar formato del archivo (CSV, Excel).
- Confirmar que las columnas críticas (IDs, Fechas, Montos) existan.
- Detectar codificación correcta (UTF-8, Latin-1).

### 2. Procesamiento con Pandas
```python
import pandas as pd

# 1. Cargar
df = pd.read_excel("manual_data.xlsx")

# 2. Normalizar Nombres
df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]

# 3. Limpiar
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df.dropna(subset=['id_cliente'], inplace=True)
```

### 3. Estrategia de Carga (Idempotencia)
Nunca insertar ciegamente. Usar una de estas estrategias:
- **Append Only**: Si son logs o eventos nuevos.
- **Staging + Merge**: Cargar a tabla temporal -> Validar -> Insertar a Producción.
- **Check + Insert**: Filtrar en Python los IDs que ya existen en DB.

### 4. Reporte
Generar siempre un resumen de la operación:
- Total filas leídas.
- Filas rechazadas (baja calidad).
- Filas insertadas.
- Filas duplicadas (ignoradas/actualizadas).

## Logs
- LOG_INFO: "integracion-manual: Recibido archivo [nombre]"
- LOG_INFO: "integracion-manual: Procesadas [N] filas válidas"
- LOG_WARN: "integracion-manual: [N] filas rechazadas por validación"
- LOG_ERROR: "integracion-manual: Error de conexión a DB"
