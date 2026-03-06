# 📚 Material de Estudio Integral: Demo Day - Plataforma Datamark

*Apuntes elaborados en base a la arquitectura, esquemas de código y flujo de datos de la plataforma.*

---

## 🏗️ 1. Arquitectura General del Sistema

La plataforma **Datamark** está concebida como un Data Analyst Automatizado para pequeños negocios (retail/ropa/calzado) en provincias del Perú. Su arquitectura se basa en las siguientes tecnologías clave:

*   **Frontend / UI:** Streamlit (`streamlit`). Permite una rápida construcción de interfaces interactivas (dashboards, editores de datos, micrófonos web).
*   **Backend:** Python puro. Se rige por un principio estricto de **simplicidad** (código directo, sin abstracciones innecesarias ni clases excesivas).
*   **Base de Datos:** PostgreSQL alojado en **Aiven**. Se utilizan 3 esquemas principales (`raw`, `staging`, `warehouse`).
*   **IA / LLM:** Google Gemini API (`google.generativeai`). Se configura con un mecanismo de *fallback* para garantizar alta disponibilidad en las extracciones de texto y auditorías.
*   **Gestión de Estado:** `st.session_state` nativo de Streamlit para el buffer temporal (*staging* en memoria) previo a la persistencia.

> **💡 Observación de Estudiante:**
> La decisión de usar Streamlit junto con PostgreSQL y esquemas bien definidos (`raw` -> `staging` -> `warehouse`) demuestra una clara orientación hacia el procesamiento analítico (OLAP), combinando de manera muy inteligente un flujo transaccional inicial (CRUD) con un pipeline ETL robusto para consumo del dashboard ejecutivo.

---

## 🗃️ 2. Flujo y Modelado de Datos (Pipeline ETL)

El sistema maneja un ciclo de vida del dato dividido en fases claras a través de scripts orquestados (`scripts/orchestrator.py`):

### Fase 1: Extracción (Extract)
Extracción de los datos transaccionales desde el esquema `raw`.
```python
def fetch_raw_data(table_name):
    try:
        engine = get_engine()
        # Búsqueda específica en el esquema 'raw'
        query = f"SELECT * FROM raw.{table_name}"
        df = pd.read_sql(query, engine)
        print(f"📦 Extraídos {len(df)} registros de raw.{table_name}")
        return df
    except Exception as e:
        print(f"❌ Error en la extracción de raw.{table_name}: {e}")
        raise e
```

### Fase 2: Transformación (Transform)
Se aplica limpieza específica según la entidad (`ventas`, `inventario`, `clientes`). Incluye eliminación de duplicados, normalización de strings (`.str.title()`, `.str.upper()`), manejo de nulos y casteo de tipos.

> **📌 Anotación Técnica:** En `clientes`, la normalización del género extrae solo la primera letra (`.str[0]`), asegurando datos limpios (`M`, `F`). El *stock* del inventario usa `.clip(lower=0)` para evitar valores negativos que puedan romper la lógica de negocio.

### Fase 3: Carga a Staging (Load)
Uso de inserciones seguras mediante la truncación de la tabla destino en una misma transacción.
```python
def upload_to_staging(df, table_name):
    try:
        engine = get_engine()
        # Transacción segura: Truncate + Append
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE staging.{table_name}"))
            if "fecha_carga" in df.columns:
               df = df.drop(columns=["fecha_carga"])
            df.to_sql(table_name, conn, schema='staging', if_exists='append', index=False)
        return True
    except Exception as e:
        return False
```

### Fase 4: Carga a Data Warehouse (Estrella)
Se alimenta un modelo dimensional con tablas de hechos (`fact_ventas`, `fact_inventario`) y dimensiones (`dim_fecha`, `dim_producto`, `dim_cliente`, `dim_medio_pago`).
*   La carga dimensional usa `INSERT INTO ... SELECT DISTINCT` desde `staging`.
*   Un paso crucial de validación es _Referential Integrity_ (`validate_referential_integrity()`), verificando que los IDs de venta existan en inventario.

---

## 🧠 3. Integración con Google Gemini (Motor de Inteligencia)

Las funciones core se encuentran en `modules/ingesta_ventas/services/extraction_service.py`.

### Sistema de Fallback Multi-Modelo
Garantiza que la plataforma no crashee si un modelo específico (ej. `2.5-flash`) encuentra problemas temporales de cuota o servicio.

```python
MODELS_BACKUP = [
    "gemini-3.1-flash-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-1.5-flash" # El más estable
]

def _generate_with_fallback(prompt: str):
    last_error = ""
    for model_name in MODELS_BACKUP:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            # ... (limpieza de markdown)
            data = json.loads(text)
            return data, model_name
        except Exception as e:
            last_error = str(e)
            continue
    raise Exception(f"Todos los modelos fallaron. Último error: {last_error}")
```

### Casos de Uso de Gemini en Datamark:
1.  **Voz / Texto Libre:** Convierte transcripciones desordenadas en un JSON estructurado (`extract_sales_data`).
2.  **Mapeo de Columnas:** En carga masiva, empareja automáticamente nombres de columnas locales del Excel del usuario con el formato requerido (`suggest_column_mapping`).
3.  **Auditoría de Negocio:** Detecta anomalías financieras o de stock ("precios raros", "duplicados") devolviendo *warnings*.

---

## ⚙️ 4. Análisis de Componentes UI

*   **Ingesta por Voz:** Integración con `streamlit_mic_recorder`. Se almacena todo temporalmente en la variable de sesión para no bombardear la base de datos hasta confirmación (Buffer/Staging en memoria).
*   **Editor de Base de Datos (CRUD):** Utiliza `st.data_editor`. Los cambios (*edited_rows*, *added_rows*, *deleted_rows*) se mapean iterativamente a bloques `UPDATE`, `INSERT`, `DELETE` con `psycopg2`.
*   **Dashboard:** Implementado con `plotly.express` y alimentado netamente desde el esquema `warehouse`. Requiere correr el orquestador ETL previamente. Utiliza una estética oscura premium (`plotly_dark`).

---

## 🎯 5. Posibles Preguntas Técnicas y Respuestas Sólidas (Simulador Demo Day)

**Q1: ¿Por qué decidieron usar un sistema de esquemas múltiple (raw, staging, warehouse) y no leer directo de las tablas transaccionales?**
> **Respuesta Estudiante Excelente:** "Leer directamente del transaccional para operaciones analíticas con agrupaciones (`GROUP BY`, métricas complejas) generaría bloqueos y problemas de rendimiento a gran escala, y expondría data "sucia". Nuestra arquitectura ETL asegura que `warehouse` contenga datos inmutables y purificados. Las dimensiones facilitan consultas rápidas y escalables para los gráficos de Plotly en tiempo real."

**Q2: En su carga de staging veo que usan `TRUNCATE TABLE`. ¿No es riesgoso perder datos ahí?**
> **Respuesta:** "No, porque `staging` es una capa estrictamente de tránsito temporal. La 'verdad' histórica reside en `raw`, y el histórico analítico en `warehouse`. Truncar `staging` nos garantiza un estado limpio en cada corrida del pipeline (Idempotencia), lo cual es más performante que un comando `DELETE` estándar y evita duplicidad silenciosa."

**Q3: ¿Cómo evitan que la aplicación se "cuelgue" si la API de Gemini no responde?**
> **Respuesta:** "Implementamos el decorador/patrón lógico `_generate_with_fallback`. Tenemos una cascada de modelos (desde el 3.1-preview hasta el 1.5-flash estable) anidados en un ciclo `try/except`. Si falla por rate-limit o inestabilidad, captura la excepción silenciosamente y reintenta automáticamente con el modelo siguiente."

**Q4: ¿Cómo manejan el choque de código en equipos o las sobre-abstracciones en Python?**
> **Respuesta:** "Adoptamos Principios de Simplicidad estrictos en `RULES.md`. Preferimos funciones imperativas claras y comprensibles con un máximo de 150 líneas por archivo, combinadas con `logs` (`logSequence`, `logInfo`). Evitamos el manejo excesivo de `try-catch` para errores no críticos, y rechazamos arquitecturas de clases sobreingeniadas. Esto hace el código ágil, legible y fácil de debuggear."

**Q5: En el Editor de Datos interactivo (CRUD), ¿cómo procesan los cambios masivos a nivel de BD de SQL?**
> **Respuesta:** "Hacemos una captura del estado del `st.data_editor` identificando `edited_rows`, `deleted_rows` y `added_rows`. Iteramos sobre diccionarios usando la función de sanitización `sanitize_val()` para convertir tipos nativos de NumPy/Pandas en tipos Python puros que el driver `psycopg2` pueda inyectar de manera segura usando parametría (`%s`) para evitar cualquier riesgo de inyección SQL."

---

## 📝 6. Conclusiones y Acuerdos de Diseño

*   **Sin Tests Formales (Unit Tests Típicos):** Por directrices del proyecto y agilidad, se prefiere la validación en desarrollo mediante el extenso sistema de validación interna y sistema de logs Custom (`libs/logger.py`).
*   **Enfoque Móvil:** Reglas de diseño mobile-first y doble interfaz implementadas en la vista para asegurar compatibilidad total en punto de venta.
*   **Resolución de Ambigüedad:** Si Gemini devuelve algo nulo que es crítico (como cliente), el sistema interviene con valores por defecto como "Anónimo" o "Desconocido" para no detener la facturación.
