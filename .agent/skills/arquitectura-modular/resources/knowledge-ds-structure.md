# Actualización: Estructura para Módulos de Data Science

Fecha: 2026-02-17
Fuente: Requerimiento del Equipo (Estructura de Análisis)

## Contexto
El equipo de Data Science propone una estructura interna específica para sus módulos, separando limpieza, métricas e insights. Esta estructura es **completamente compatible** con la Arquitectura Modular, siempre que viva DENTRO de un módulo.

## Patrón Recomendado: Módulo de Análisis

Para features intensivas en datos (ej: Dashboards, Modelos ML), se recomienda esta estructura interna dentro de `modules/[nombre_feature]/`:

```text
modules/analisis_ventas/       <-- Nombre del Módulo
├── app.py                     <-- Entry Point (Streamlit UI)
├── analysis/                  <-- Lógica de Negocio (Data Science)
│   ├── cleaning.py            <-- Limpieza y normalización
│   ├── metrics.py             <-- Cálculo de KPIs
│   └── insights.py            <-- Generación de textos/reglas
├── database/                  <-- Acceso a Datos (Local del módulo)
│   ├── models.py              <-- Pydantic models / Clases
│   └── queries.py             <-- SQL específico de este módulo
└── components/                <-- Gráficos Específicos
```

## Adaptación de Reglas
1.  **Conexión a BD:** `database/connection.py` NO debe existir dentro del módulo si es la conexión global. Debe importarse de `libs/db_connection.py`.
    - ❌ `modules/analisis/database/connection.py`
    - ✅ `from libs.db_connection import get_db_connection`

2.  **App.py:** El `app.py` listado es el entry point *local* del módulo, que será invocado por `pages/XX_Analisis.py`.
