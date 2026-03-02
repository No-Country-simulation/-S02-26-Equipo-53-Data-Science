# Actualización: Mejores Prácticas para Equipos en Streamlit

Fecha: 2026-02-17
Fuente: Experiencia en Desarrollo Colaborativo

## 1. Gestión del Estado (Session State)
Cuando múltiples desarrolladores usan `st.session_state`, las colisiones de nombres son comunes (ej: ambos usan `counter` o `input_val`).

**Regla:** Todo key en session_state debe tener un prefijo único por módulo.
- ❌ `st.session_state['count']`
- ✅ `st.session_state['sales_count']` o `st.session_state['hr_employee_list']`

**Patrón de Fábrica de Estado:**
Cada módulo debe tener una función `init_state()` en su `app.py` o `logic.py` que inicialice sus variables solo si no existen.

## 2. Gestión de Dependencias
- **Librerías Globales:** Si una librería se usa en todo el proyecto (ej: `pandas`, `psycopg2`), va en `requirements.txt` raíz.
- **Librerías Locales:** Si un módulo necesita una librería específica rara, se puede instalar, pero debe documentarse en un `requirements.txt` dentro de `modules/nombre_modulo/` (aunque no se instale automático, sirve de documentación).

## 3. Testing Unitario Modular
Streamlit es difícil de testear end-to-end, pero la lógica de negocio NO debe estar acoplada a la UI.
- ❌ Lógica dentro de `if st.button(): ...`
- ✅ Lógica en `modules/sales/services.py` que retorna datos. `app.py` solo pinta.

Esto permite testear `services.py` con `pytest` sin levantar el servidor de Streamlit.

## 4. Git Flow para Streamlit
- **Ramas por Feature:** `feature/sales-ingestion`, `feature/hr-dashboard`.
- **Pull Requests:** Antes de mergear a `develop`, otro desarrollador debe probar la "Page" del módulo.
- **Conflictos en `.streamlit/config.toml`:** Evitar editar configuración global a menos que sea consenso de equipo.
