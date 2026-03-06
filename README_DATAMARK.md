# 📊 DATAMARK - Plataforma de Automatización de Ventas e Inventarios

## 🚀 Descripción del Proyecto

**DATAMARK** es una solución SaaS B2B en etapa MVP diseñada para
pequeños negocios de ropa y calzado en provincias del Perú.

El objetivo es **automatizar la gestión de ventas, inventarios y
clientes**, centralizando datos que normalmente se manejan en Excel o de
forma manual, y transformarlos en dashboards claros para la toma de
decisiones.

------------------------------------------------------------------------

# 🎯 Problema que Resuelve

Muchos pequeños negocios:

-   Gestionan ventas en Excel
-   No controlan correctamente inventarios
-   No tienen métricas claras
-   Cometen errores manuales
-   Toman decisiones sin datos estructurados

DATAMARK busca:

✔ Centralizar datos

✔ Automatizar limpieza y transformación

✔ Visualizar KPIs en dashboards

✔ Reducir errores operativos

------------------------------------------------------------------------

# 🏗 Arquitectura del Proyecto

El flujo actual del sistema sigue una arquitectura tipo Data Pipeline:

    Ingreso Manual / Excel
            ↓
    Schema RAW (Datos crudos)
            ↓
    Schema STAGING (Limpieza y validación)
            ↓
    Schema WAREHOUSE (Modelo final optimizado)
            ↓
    Dashboard

## 🔎 Diagrama de Arquitectura

![Flujo del Data Pipeline](images/flujo.png)

Este diagrama muestra cómo los datos fluyen desde la ingesta inicial
hasta la capa analítica utilizada por el dashboard en Streamlit.

------------------------------------------------------------------------

# 🧱 Modelo Dimensional (Data Warehouse)

El schema `warehouse` implementa un modelo tipo **Star Schema**,
optimizado para análisis OLAP.

## 📊 Diagrama del Modelo

![Modelo OLAP](images/modelado_Olap.png)

### Tablas de Hechos:

-   fact_ventas
-   fact_inventario

### Tablas Dimensión:

-   dim_cliente
-   dim_producto
-   dim_fecha
-   dim_medio_pago

Este modelo permite:

✔ Análisis por cliente

✔ Análisis por producto

✔ Análisis temporal

✔ Análisis por medio de pago

------------------------------------------------------------------------

# 🗂 Estructura del Proyecto

    Proyecto/
    │
    ├── data/                          
    │   ├── dummy/      
    │     │
    ├── libs/                             # 🧱 Core Técnico (Compartido)
    │   ├── db_connection.py              # Singleton de conexión a Aiven PostgreSQL
    │   ├── logger.py                     # Sistema de trazas (logInfo, logError) unificado
    │   ├── models.py                     # Centralización de consultas/modelos base
    │   └── styles/
    │
    ├── modules/                          # 🧠 Cerebro del Proyecto (Micro-Arquitecturas)
    │   ├── dashboard/                    # Motor de Business Intelligence
    │   │   ├── _init_.py                 
    │   │   └── dashboard_logic.py        # Procesamiento Pandas para gráficos y KPIs en vivo
    │   │
    │   ├── gestion_dueño/                # Panel Administrativo
    │   │   ├── components/               # UI de tablas y métricas owner-level
    │   │   └── services/                 # Gestores de eliminación u operaciones destructivas
    │   │
    │   └── ingesta_ventas/               # 🎙️ Core Transaccional e IA
    │       ├── app.py                    # Orquestador del módulo
    │       ├── components/               # Interfaces Modulares
    │       │   ├── voice_input.py        # Grabadora web y procesamiento NLP
    │       │   ├── mass_upload.py        # Lector de Excel y formateador tabular
    │       │   ├── manual_input.py       # Formularios Streamlit tradicionales
    │       │   └── database_viewer.py    # El "CRUD Web" interactivo (st.data_editor)
    │       └── services/                 # Conexiones con el Mundo Exterior
    │           ├── db_service.py         # Consultas de ambigüedad, match exacto/fuzzy y triggers
    │           ├── extraction_service.py # Comunicación con API Gemini 2.5 Flash
    │           └── state_manager.py      # Gestor transversal de st.session_state
    │
    ├── pages/                            # 🌐 Front-Door (Ruteo de Streamlit)
    │   ├── 01_Ingesta_Ventas.py          # Enruta a modules/ingesta_ventas/app.py
    │   ├── 02_Gestion_Dueño.py           # Enruta a modules/gestion_dueño
    │   └── dashboard.py                  # Enruta a modules/dashboard
    │
    ├── scripts/                          # 🛠️ Herramientas de Línea de Comandos (DevOps)
    │   ├── etl/
    │   ├── check_permissions.py        
    │   ├── cleanup_libs.py             
    │   ├── ingest_excel_data.py 
    │   ├── inspect_db.py      
    │   ├── list_tables.py             
    │   ├── orchestrador.py
    │   ├── populate_mock_db.py    
    │   └── test_structure.py
    │
    ├── test_data/                          
    │   └── ventas_muestra.csv       
    ├── .env.example                      # Plantilla de secretos requeridos (Aiven / Gemini API)
    ├── .gitignore                 
    ├── main.py                           # Entrypoint de Streamlit corriendo el Landing Page
    ├── requirements.txt                  # Strict list de dependencias Python (psycopg2, streamlit, etc)
    ├── main.py                           # Entrypoint de Streamlit corriendo el Landing Page    
    └── README.md                         # Este manifiesto global
       
  

# 🛠 Tecnologías Utilizadas

### Backend / ETL

-   Python
-   Pandas
-   SQLAlchemy
-   PostgreSQL

### Base de Datos

-   PostgreSQL
-   DBeaver

### Control de Versiones

-   Git
-   GitHub

### Automatización de flujo de datos

-   Archivo orchetrator.py donde defines un flujo de trabajo compuesto por tareas encadenadas.

------------------------------------------------------------------------

# 🔄 Flujo ETL Implementado

El proceso ETL actual realiza:

### 1️⃣ Extract (RAW)

-   Lectura de la capa Raw de la base de datos (Desde la aplicación el usuario inserta los datos en la capa Raw)

### 2️⃣ Transform

-   Limpieza de valores nulos
-   Corrección de tipos de datos
-   Validación de registros inconsistentes

### 3️⃣  Load (STAGING)

-   Inserción directa al schema `staging`

### 4️⃣ Load Final (WAREHOUSE)

-   Lectura de la capa staging, organización y carga de los datos en el modelo dimensional de la capa warehouse
-   Inserción en tablas optimizadas para análisis.

------------------------------------------------------------------------

# 📊 Estado Actual del Proyecto

✔ Conexión exitosa a PostgreSQL

✔ Creación de schemas: raw, staging, warehouse

✔ Inserción de datos desde CSV

✔ Script ETL funcional

✔ Visualización en DBeaver

✔ Repositorio conectado a GitHub

✔ "Pipeline básico de integración continua"

------------------------------------------------------------------------

# ▶️ Cómo Ejecutar el Proyecto

## 1️⃣ Clonar repositorio

``` bash
git clone https://github.com/No-Country-simulation/-S02-26-Equipo-53-Data-Science.git
```

## 2️⃣ Crear entorno virtual

``` bash
python -m venv venv
venv\Scripts\activate
```

## 3️⃣ Instalar dependencias

``` bash
pip install -r requirements.txt
```

## 4️⃣ Ejecutar la Aplicación

``` bash
streamlit run main.py
```

------------------------------------------------------------------------

# 🔐 Variables de Entorno

Se recomienda usar un archivo `.env`:

    DB_HOST= "Colocar aqui el host"
    DB_PORT= "Colocar aqui el puerto"
    DB_NAME= "Colocar aqui el nombre de la base de datos"
    DB_USER= "Colocar aqui el usuario"
    DB_PASSWORD= "Colocar aqui la contraseña"
    GEMINI_API_KEY= "Colocar aqui la API"

------------------------------------------------------------------------

# 🧪 Próximos Pasos

-   Integración con frontend (Streamlit o React)
-   Automatización completa desde botón "Ver Dashboard"
-   Implementación de pruebas automatizadas
-   Despliegue en la nube
-   Autenticación de usuarios

------------------------------------------------------------------------

# 📈 Impacto Esperado

-   Reducción de errores manuales
-   Mayor control de inventarios
-   Visualización clara de ventas
-   Mejores decisiones comerciales

------------------------------------------------------------------------

# 👩‍💻 Autores

El proyecto, ha sido desarrollado como parte de un desafío técnico enfocado en
automatización y análisis de datos para pequeñas empresas, por:

-   Dabalos Carla
-   Estrada Leomar
-   Paye Cahui Oscar Ferando
-   Tantarico Minchola Galia Lizbeth




