# 🗄️ Estrategia de Base de Datos

DATAMARK utiliza **Aiven for PostgreSQL** como motor central, implementando una arquitectura de esquemas para separar procesos transaccionales de analíticos.

## 📐 Modelo de Datos

### Esquema RAW (OLTP)
Diseñado para la captura rápida y segura de transacciones diarias.
- `ventas_raw`: Registro de cada venta individual.
- `inventario_raw`: Catálogo central de productos y control de stock.
- `clientes_raw`: Directorio de clientes.

### Esquema Warehouse (OLAP)
Implementa un modelo de **Estrella (Star Schema)** optimizado para reportes.
- **Hechos (`fact`)**: `ventas_warehouse`
- **Dimensiones (`dim`)**: `dim_producto`, `dim_cliente`, `dim_tiempo`.

## 🔒 Integridad y Seguridad
- **Validación Multi-capa**: Las ventas se verifican contra el stock actual antes de ser procesadas.
- **Conexiones Seguras**: Uso de SSL y variables de entorno para credenciales.
- **Manejo de Tipos**: Conversión explícita de tipos de datos (NumPy/Pandas a Python nativo) para compatibilidad con Psycopg2.
