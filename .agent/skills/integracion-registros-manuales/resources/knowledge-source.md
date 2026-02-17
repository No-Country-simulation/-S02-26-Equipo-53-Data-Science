# Fuente de Conocimiento: Integración de Registros Manuales

**Fecha de Captura:** 2026-02-12
**Tema:** Integración de datos manuales (Excel/CSV) a Base de Datos General (SQL)
**Fuentes:** Búsqueda Web (Pandas, SQLAlchemy Best Practices)

## Resumen de Mejores Prácticas

La integración de datos manuales requiere un enfoque riguroso en **Calidad de Datos**, **Gobierno** y **Automatización**.

### 1. Preparación de Datos (Pandas)
- **Lectura**: Usar `pd.read_csv()` o `pd.read_excel()` para cargar datos.
- **Estandarización**: Asegurar que los nombres de columnas coincidan con la DB (`df.rename`).
- **Limpieza**: Manejar valores nulos (`fillna`), eliminar duplicados (`drop_duplicates`), y validar tipos de datos.
- **Validación**: Verificar que los datos cumplan las reglas de negocio antes de intentar la carga.

### 2. Conexión a Base de Datos (SQLAlchemy)
- Utilizar `SQLAlchemy` para crear conexiones seguras y eficientes.
- Configurar un `engine` con las credenciales adecuadas.

### 3. Estrategia de Carga (Merging)
- **Método `to_sql`**: Usar `if_exists='append'` para agregar nuevos registros.
- **Manejo de Duplicados**:
    - **Upsert**: Si la DB lo soporta (PostgreSQL `ON CONFLICT`, MySQL `ON DUPLICATE KEY`).
    - **Pre-validación**: Consultar IDs existentes antes de insertar para filtrar duplicados.
    - **Tabla Temporal**: Cargar a una tabla 'staging' y luego hacer MERGE con SQL nativo.

### 4. Gobierno y Seguridad
- **Backups**: Siempre tener respaldo antes de operaciones masivas.
- **Transacciones**: Usar transacciones SQL para asegurar atomicidad (todo o nada).
- **Logs**: Registrar el resultado de la operación (filas insertadas, errores).

## Referencias Técnicas
- Pandas `to_sql`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
- SQLAlchemy Engine: https://docs.sqlalchemy.org/en/20/core/engines.html
