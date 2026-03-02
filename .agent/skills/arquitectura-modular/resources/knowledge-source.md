# Arquitectura Modular en Streamlit

## Contexto
El desarrollo de aplicaciones Streamlit en equipo suele enfrentar problemas de organización cuando el proyecto crece. El patrón de "Single Script" (todo en un archivo) o "Flat Pages" (todo en la raíz pages/) no escala bien.

## Principios de Diseño

### 1. Separación de Responsabilidades (SoC)
- **Navegación (pages/)**: Solo define la estructura del menú lateral y la configuración básica de la página. No contiene lógica de negocio.
- **Lógica (modules/)**: Contiene la implementación real. Cada carpeta es un dominio de negocio (Ventas, RRHH, Logística).
- **Infraestructura (libs/)**: Código agnóstico al negocio (Conexión a BD, Logging, Estilos Globales).

### 2. Aislamiento de Conflictos
Al asignar una carpeta `modules/X` a cada desarrollador o squad, los conflictos de git se reducen drásticamente. Si dos personas tocan `app.py` en carpetas diferentes, git lo maneja sin problemas.

### 3. Reusabilidad
Los componentes en `modules/X/components` pueden ser movidos a `libs/components` si se descubre que son útiles para otros módulos, promoviendo una refactorización orgánica ("Harvesting").

## Ejemplo Práctico

Si Juan hace "Ventas" y María hace "Recursos Humanos":

**Juan crea:**
- `modules/sales/ingestion.py`
- `pages/1_Ingreso_Ventas.py` (que llama a `ingestion.py`)

**María crea:**
- `modules/hr/employees.py`
- `pages/2_Gestion_Personal.py` (que llama a `employees.py`)

Ambos pueden trabajar en paralelo. El único punto de conflicto potencial es `libs/db_connection.py` si ambos lo editan, pero eso debe ser estable.
