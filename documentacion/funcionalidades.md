# 🚀 Funcionalidades y Capacidades

![Estado](https://img.shields.io/badge/Estado-Producción-brightgreen?style=flat-square)
![Interactividad](https://img.shields.io/badge/Interactividad-Alta-orange?style=flat-square)
![Escalabilidad](https://img.shields.io/badge/Escalabilidad-Total-blue?style=flat-square)


## 🎨 Visión General
DATAMARK no es solo un registrador de datos; es un asistente de negocio proactivo. Cada módulo ha sido diseñado pensando en la eficiencia operativa y la claridad visual.

---

## 🎙️ Ingesta Inteligente (Smart Ingestion)
Es el componente estrella que elimina la barrera de entrada tecnológica para el usuario.

```mermaid
graph LR
    V[Voz] --> AI[Extraer Entidades]
    E[Excel] --> M[Mapear Columnas]
    Man[Manual] --> F[Insertar Directo]
    
    AI --> Match{¿Producto Existe?}
    Match -->|Sí| OK[Confirmar Venta]
    Match -->|No| Sug[Sugerencias Fuzzy]
```

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
Visualización de alto impacto para la toma de decisiones basada en datos, no en intuiciones.

```mermaid
pie title Distribución de Ventas por Categoría
    "Ropa" : 45
    "Calzado" : 35
    "Accesorios" : 20
```

### KPIs Soportados:
- **Revenue Diario/Semanal/Mensual**.
- **Churn Rate de Clientes**.
- **Stock de Seguridad**: Alertas automáticas cuando un producto baja de cierto umbral.
- **Captación**: Análisis de qué canales (Voz vs Manual) son más efectivos.

---
> [!TIP]
> Puedes extender las capacidades del dashboard agregando consultas SQL personalizadas en `modules/dashboard/dashboard_logic.py`.
