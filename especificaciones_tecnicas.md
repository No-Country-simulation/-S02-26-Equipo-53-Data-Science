# 📚 Material de Estudio Técnico: Especificaciones y Roles - Demo Day Datamark

*Apuntes avanzados sobre infraestructura, capacidades, flujo de datos y la orquestación de roles en el desarrollo de la plataforma.*

---

## ☁️ 1. Arquitectura de Infraestructura (Cloud & Base de Datos)

La plataforma Datamark se sostiene sobre una arquitectura distribuida ligera, enfocada en minimizar costos operativos mientras garantiza alta disponibilidad para pequeños negocios.

### 🐘 Aiven for PostgreSQL (Capa de Persistencia)
*   **Tier / Tamaño de Nodo:** *Hobbyist* o *Startup* (típicamente 1 CPU, 1 GB RAM en su capa gratuita).
*   **Almacenamiento (Base de Datos):** El nivel gratuito (`Hobbyist`) otorga actualmente **1 GB de almacenamiento** (anteriormente 5 GB). Considerando que una transacción de venta *raw* en texto plano pesa unos pocos bytes (~150-300 bytes), 1 GB puede almacenar iterativamente **millones de registros** iniciales.
*   **Conexiones Concurrentes:** Limitadas a un máximo de 20 (`max_connections`) sin pooler de conexiones en el tier gratuito. El uso de validaciones como `pool_pre_ping=True` de SQLAlchemy asegura que no haya conexiones fantasma consumiendo recursos limitados.

### 🌐 Streamlit Community Cloud (Capa de Presentación)
*   **Asignación de Recursos:** Los contenedores estándar en Streamlit Cloud asignan entre **0.078 y 2 cores de CPU**, y una memoria RAM garantizada de **690 MB con ráfagas hasta 2.7 GB** (aunque la regla general es mantener el uso debajo de 1 GB).
*   **Limitaciones (Out of Memory - OOM):** Si el buffer en memoria de pandas (el *staging* `st.session_state`) sobrepasa la RAM asignada al procesar un Excel gigantesco de golpe, la app podría reiniciarse con un error de recursos ("*This app has gone over its resource limits*"). Por eso, las subidas masivas se procesan y luego se inyectan a la BD vaciando el estado (Chunking & Caching).

> **💡 Apunte de Estudiante Excelente:**
> Separar el cómputo (Streamlit Cloud) del almacenamiento (Aiven PostgreSQL) es una decisión brillante de **Desacoplamiento (Decoupling)**. Si Streamlit se cae, la data transaccional sigue viva y segura en Aiven.

---

## 🧠 2. Especificaciones del Motor de IA (Google Gemini API)

La Inteligencia Artificial no es un simple chat; actúa como un microservicio de extracción de entidades (NER) y razonamiento semántico.

*   **Modelos Configurados en Fallback:**
    *   `gemini-3.1-flash-preview` / `gemini-3-flash-preview`
    *   `gemini-2.5-flash`
    *   `gemini-1.5-flash` (Estable)
*   **Ventana de Contexto (Tokens):** El tier gratuito actual de Gemini 1.5 Flash soporta hasta **1 millón de tokens de entrada**. Esto significa que teóricamente podrías enviarle un libro entero transcrito por voz.
*   **Límites de Salida (Output):** Suele rondar los **8,192 tokens** por respuesta. Más que suficiente para estructurar arrays JSON de ventas por tickets masivos.
*   **Capacity y RPM (Requests Per Minute):** El tier gratuito de Gemini 1.5 Flash ofrece un sorprendente límite de **1,000 RPM (Requests per minute)** y **250,000 TPM (Tokens per minute)**. Esto asegura una altísima disponibilidad para carga rápida, aunque si se supera por ráfagas intensas, el script `_generate_with_fallback` intentará iterar la lista de respaldo.

---

## 🔄 3. El Flujo de Datos (Data Flow Pipeline)

El ciclo de vida del dato desde su captura hasta el dashboard ejecutivo.

1.  **Ingesta (Punto de Venta/Dueño):** El usuario dicta una venta ("*Vendí dos blusas rojas talla S por 50 soles a María de Gamarra*").
2.  **Motor LLM (Inferencia):** Gemini procesa la cadena de audio->texto, mapea las variables requeridas (producto, cantidad, precio, cliente) a un JSON estructurado e infiere variables no explícitas (categoría, fecha=hoy).
3.  **Memoria Volátil (Staging local):** Se almacena temporalmente en el `st.session_state` de la sesión activa de Streamlit para revisión humana (Data Editor).
4.  **Capa RAW (Aiven BD):** Al confirmar, un script (`psycopg2`) inserta datos inmutables y crudos en `ventas_raw`, realizando validaciones estrictas *Acid* y cruzando contra `inventario_raw` para el descuento de stocks vía SQL Transaccional.
5.  **Capa ETL & Warehouse (Orquestación `orchestrator.py`):** Un proceso a demanda ejecuta:
    *   **Extract (`extract.py`):** Lee transaccionalmente los tres esquemas `raw` de forma independiente a DataFrames de Pandas (`fetch_raw_data`).
    *   **Transform (`transform.py`):** Usando `pandas`, se barren los DataFrames: elimina duplicados mediante `drop_duplicates`, aplica normalizaciones de caracteres (`.str.strip().str.title()`), restringe números negativos del inventario con `.clip(lower=0)`, y parsea fechas nulas robustamente. Pandas se comporta excepcionalmente rápido porque la manipulación vectorial reside en RAM (`server-side`).
    *   **Load (to Staging BD) (`load.py`):** Antes de la ingesta en bloque, trunca (`TRUNCATE`) e inserta temporalmente en el esquema `staging`. Es vital que suceda dentro de un solo transaction block para evitar lectura sucia.
    *   **Load (to Warehouse) (`warehouse.py`):** Cruza dimensiones (`dim_cliente`, `dim_producto`) iterativamente y construye tablas de hechos masivas (`fact_ventas`), apoyado en validaciones previas de integridad referencial obligatoria (`validation.py`).
6.  **Consumo Analítico (Analytics):** Los Dashboards en `dashboard_logic.py` no conectan con raw; atacan directamente a `warehouse` con queries ligeras pre-agregadas. Utilizando `plotly.express`, se confeccionan Treemaps, Line Charts y Bar Charts segmentados, ofreciendo alta densidad de información gráfica inmediata (Ej: Distribución `Ventas por Talla` y Top Performers).

---

## 🎭 4. Intersección de Roles (El Tridente de Datos)

El éxito de la plataforma reside en cómo cubre orgánicamente las tres principales ramas del espectro de datos:

### 🛠️ Data Engineer (Ingeniería de Datos)
*   **Responsabilidad en Proyecto:** Diseño del ecosistema multi-esquema (`raw`, `staging`, `warehouse`), orquestación de la tubería ETL/ELT (`orchestrator.py`). Programación de validaciones automáticas de integridad referencial (`validation.py`) para garantizar que no existan Ventas con IDs de Productos huérfanos. Manejo de Pool de conexiones con SQLAlchemy.
*   **Valor Aportado:** Garantiza que los datos transicionen limpiamente de "Caos transaccional" a "Verdad única reportable", escalen bajo demanda y que el DW no corrompa métricas financieras.

### 🔬 Data Scientist (Ciencia de Datos / IA Aplicada)
*   **Responsabilidad en Proyecto:** Implementación de la inteligencia "Zero-Shot" con Gemini. Mapeo probabilístico para extraer entidades asertivas de un dictado caótico, además del sistema Multi-Modelo de *fallback* para alta disponibilidad.
*   **Valor Aportado:** Transforma datos desestructurados o cualitativos brutos (audio, texto libre o PDFs en lote) a un formato tabular estructurado en el sistema transaccional. Enseña a que el sistema "razone" el negocio (Ej: Detección de *Anomalies* y *Antipatterns* en ventas cruzadas).

### 📊 Data Analyst (Análisis de Datos)
*   **Responsabilidad en Proyecto:** Explotación de los esquemas estrella (`warehouse`) para confeccionar el Tablero Ejecutivo (`dashboard_logic.py`). Redacción de consultas SQL con filtros por componentes Streamlit y agregaciones dinámicas, convertidas en gráficos impactantes con `Plotly` (dark theme adaptativo).
*   **Valor Aportado:** Democratiza los datos de la base de datos hacia los dueños del negocio. Traduce millones de transacciones a KPI visuales directos (Ticket Promedio, Rendimiento de Stock vs Demanda).

---

## 🎯 5. Preguntas de Defensa (Demo Day)

**Q1: ¿Por qué Pandas en transformación ETL en lugar de dbt (Data Build Tool)?**
> **A:** "El proyecto exige alta velocidad de interacción con memorias locales (Staging en Streamlit). Pandas opera en RAM antes del reenvío de datos y ofrece flexibilidades perfectas en manipulación de strings y fechas. dbt es excelente, pero añade sobrecarga y complejidad innecesaria (`overhead`) para un sistema en fase temprana (`Startup MVP`) donde el volumen de datos en MB no justifica aún procesamiento masivo distribuido tipo Spark o motores Snowflake."

**Q2: ¿En qué escenario escalarían vertical u horizontalmente su base de datos Aiven?**
> **A:** "**Data Engineering View:** Escalaríamos verticalmente (más CPU/RAM para la db) primero si notamos cuellos de botella procesando el `GROUP BY` de los joins en el `warehouse` una vez que tengamos millones de tuplas. Escalaríamos horizontalmente agregando réplicas de lectura (Read Replicas) si observamos latencia porque muchos usuarios acceden al dashboard analítico de forma simultánea, liberando al nodo principal (`master`) para dedicarse a las escrituras CRUD del `raw`."

**Q3: Teniendo restricciones de hardware en Streamlit Cloud, ¿qué pasa si cargan 1 millón de filas y saturan el RAM?**
> **A:** "**Data Science & Engine View:** Aplicamos un enfoque de segmentación (`Chunking`). La carga masiva procesaría el archivo en trozos pequeños iterativos. Además, delegaríamos la pre-limpieza y agregación principal directamente al motor de base que suele ser mucho más robusto usando `SQL` en vez de cargar 1 millón de filas directamente al `DataFrame` de Streamlit que se sobrepasaría de sus 1GB."

**Q4: ¿Cómo justifica el Data Analyst el diseño del modelo Estrella (Star Schema) vs. SnowFlake (Copo de nieve)?**
> **A:** "El Star Schema deconstruye la Venta (`fact_ventas`) con ramificaciones rápidas directas a los identificadores `dim`. Eso ahorra pasos computacionales (`JOIN` enlazados de copo de nieve) resultando en queries *ad-hoc* instantáneos para Plotly y mitigando el retraso UI (User Interface Delay). Además, en entornos de retail local un esquema totalmente normalizado tipo snowflake excede la sofisticación real necesaria."

**Q5: En el contexto de Calidad de Datos (Data Quality), ¿cómo aborda Ingeniería la integridad referencial antes del Warehouse?**
> **A:** "**Data Engineering View:** Lo manejamos con el módulo `validation.py` en la orquestación. Este paso extrae los IDs únicos de ventas desde el staging y hace un match contra los IDs en inventario antes de hacer el merge en la tabla de Fechos (Fact). Si detecta inconsistencias (como una venta de un producto fantasma o sin registrar), detiene la ejecución del Warehouse para evitar ensuciar los analíticos y reporta la alerta al pipeline."

**Q6: ¿Por qué elegir Plotly sobre librerías nativas como Matplotlib o Altair para los gráficos del Data Analyst?**
> **A:** "**Data Analyst View:** Plotly es superior en entornos interactivos web como Streamlit porque genera gráficos basados en React.js por detrás (`D3.js`). A diferencia de correar imágenes estáticas en `.png` mediante Matplotlib, Plotly nos entrega de forma nativa Tooltips dinámicos al pasar el ratón (*hover*), zoom de ejes y selecciones sin necesidad de codear callbacks manuales pesados, permitiendo una inmersión visual más profunda para los dueños."
