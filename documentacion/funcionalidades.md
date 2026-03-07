# 🚀 Funcionalidades y Capacidades

![Estado](https://img.shields.io/badge/Estado-Producción-brightgreen?style=flat-square)
![Interactividad](https://img.shields.io/badge/Interactividad-Alta-orange?style=flat-square)
![Escalabilidad](https://img.shields.io/badge/Escalabilidad-Total-blue?style=flat-square)


## 🎨 Visión General
DATAMARK no es solo un registrador de datos; es un asistente de negocio proactivo. Cada módulo ha sido diseñado pensando en la eficiencia operativa y la claridad visual.

---

## 🎙️ Tipos de Ingesta Inteligente
Soportamos múltiples canales para asegurar que ningún dato se pierda:

*   **Canal Audio**: Procesamiento continuo de voz a datos.
*   **Canal Masivo**: Inyección de lotes históricos vía Excel/CSV.
*   **Canal Admin**: Formularios de alta velocidad para ajustes rápidos.

---

### Características Clave:
- **Detección Dinámica**: Identifica automáticamente si lo que el usuario dice es una venta o un movimiento de inventario.
- **Mapeo Automático**: Durante la carga masiva, la IA predice qué columna del Excel del usuario se refiere al "Precio" o "Producto", incluso con nombres de columna diferentes.

---

## 🛠️ Gestión Transaccional y Auditoría
Un panel de control robusto para la supervisión diaria.

| Función | Herramienta | Beneficio |
| :--- | :--- | :--- |
| **CRUD Directo** | `st.data_editor` | Edición masiva con un solo clic. |
| **Paginación Dinámica** | SQL `LIMIT/OFFSET` | Navegación fluida en miles de registros. |
| **Auditoría IA** | Gemini Scan | Detección automática de anomalías de precios. |

---

## 📈 Power Dashboards (BI)
Visualización de KPIs para la toma de decisiones:

*   **Ventas por Categoría**: Comparativa dinámica (Eje: Ropa 45%, Calzado 35%, Accesorios 20%).
*   **Revenue Temporal**: Seguimiento de ingresos diarios y mensuales.
*   **Balance de Inventario**: Alertas de stock crítico.

---

### KPIs Soportados:
- **Revenue Diario/Semanal/Mensual**.
- **Churn Rate de Clientes**.
- **Stock de Seguridad**: Alertas automáticas cuando un producto baja de cierto umbral.
- **Captación**: Análisis de qué canales (Voz vs Manual) son más efectivos.

---
> [!TIP]
> Puedes extender las capacidades del dashboard agregando consultas SQL personalizadas en `modules/dashboard/dashboard_logic.py`.
