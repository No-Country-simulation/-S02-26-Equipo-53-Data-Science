---
description: Estándares de arquitectura modular para evitar conflictos en equipos de desarrollo Streamlit
---

# Skill: Arquitectura Modular para Equipos (Streamlit)

Este skill define la estructura de carpetas y patrones de código obligatorios para trabajar en equipo sin conflictos.

## Problema
Si todos trabajan en `main.py` o en una carpeta genérica `src/`, ocurren conflictos de fusión (merge conflicts) y el código se vuelve inmanejable.

## Solución: Patrón de Módulos Aislados

Cada nueva funcionalidad debe ser un **módulo independiente** encapsulado en su propia carpeta.

### Estructura Recomendada

```
proyecto/
├── main.py                  # Entry Point (Landing Page global)
├── pages/                   # Wrappers de Streamlit (Solo importan módulos)
│   ├── 01_Ventas.py         -> Importa modules.ventas.app
│   └── 02_Inventario.py     -> Importa modules.inventario.app
├── modules/                 # CÓDIGO REAL (Aquí trabaja cada dev)
│   ├── ventas/              # Tu espacio de trabajo
│   │   ├── app.py           # Tu "main" local
│   │   ├── services.py      # Tus lógicas
│   │   └── components/      # Tus widgets
│   ├── inventario/          # Espacio de otro dev
│   │   └── app.py
│   └── analisis/            # Estructura Data Science (Opción Avanzada)
│       ├── app.py
│       ├── analysis/        # Lógica de DS
│       │   ├── cleaning.py
│       │   ├── metrics.py
│       │   └── insights.py
│       └── database/        # Modelos locales (NO conexión)
│           └── models.py
└── libs/                    # Código compartido (Utils, DB Connection)
```

## Reglas de Oro

1.  **NO modificar `main.py`** salvo para agregar navegación global.
2.  **NO poner código lógico en `pages/`**. Los archivos en `pages/` deben tener menos de 10 líneas (solo configuración e importación).
3.  **Tu código vive en `modules/[tu_feature]/`**. Ahí eres dueño y señor.
4.  **Usa `libs/` para lo común**. Si necesitas conectar a BD, usa el conector compartido en `libs/`, no crees el tuyo propio.

## Cómo implementar una nueva feature

1.  Crea la carpeta `modules/[nombre_feature]`.
2.  Desarrolla todo ahí (`app.py`, `services.py`).
3.  Crea un archivo wrapper en `pages/[XX]_[Nombre_Feature].py`.
4.  Importa tu módulo en el wrapper:
    ```python
    import modules.nombre_feature.app as feature
    feature.main()
    ```

## Mejores Prácticas Avanzadas

### 1. Session State (Evitar Colisiones)
Usa prefijos únicos para las claves en `st.session_state`.
- ❌ `st.session_state['counter']`
- ✅ `st.session_state['sales_counter']`

### 2. Testing Unitario
Desacopla la lógica de la UI. Escribe funciones puras en `services.py` que retornen datos, y testealas con `pytest` sin necesidad de levantar Streamlit.

### 3. Git Flow
- Crea ramas por feature (`feature/ventas`).
- Haz Pull Request hacia `develop`.
- Si tocas `libs/`, avisa al equipo.
