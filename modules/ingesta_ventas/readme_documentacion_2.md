# DATAMARK - Plataforma de Data Analyst Automatizado

## 🏆 Insignias
![Python](https://img.shields.io/badge/Python-3.13-3776ab?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791?style=flat-square&logo=postgresql&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2+-150458?style=flat-square&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production-brightgreen?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0-blue?style=flat-square)

## 📌 Índice
- [Descripción](#-descripción)
- [Estado del Proyecto](#-estado-del-proyecto)
- [Funciones y Aplicaciones](#-funciones-y-aplicaciones)
- [Características Principales](#-características-principales)
- [Arquitectura](#-arquitectura)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Base de Datos](#-base-de-datos)

## 📙 Descripción
Plataforma integral de gestión comercial diseñada para modernizar tiendas minoristas en provincias del Perú. Actúa como un Analista de Datos automatizado que captura interacciones diarias de Ventas e Inventario a través de voz (NLP), formularios o Excel, garantizando la integridad referencial en tiempo real antes de consolidarlas en un Data Warehouse PostgreSQL.

## 🟢 Estado del Proyecto
Actualmente el proyecto y su módulo núcleo (**Ingesta de Ventas**) se encuentra en **producción**. La capa transaccional está 100% estabilizada con cruces relacionales por IA y Regex local.
**Versión**: 1.0  
**Última actualización**: Marzo 2026

## 🎥 Funciones y Aplicaciones
- **Ingesta por Voz**: Reconocimiento de lenguaje natural (NLP) dictado con inferencia de variantes y Auto-Creador de Clientes.
- **Carga Masiva Analítica**: Subida masiva de Excels históricos con limpieza determinística ($0 API Limit) y cruce exacto/fuzzy.
- **Formularios Robustos**: Ingreso manual parametrizado con protección anti-cuelgues (NaN Math Sanitation).
- **CRUD Visual Paginado**: Edición directa y segura de la capa Raw desde el navegador web sin necesidad de escribir SQL.
- **Prevención de Colisiones**: Descuentos transaccionales seguros (Atomicidad) que bloquean ventas sin inventario físico comprobado.

## 🎯 Características Principales
- **Inteligencia Híbrida**: Combina la libertad del LLM Gemini Flash para el NLP con la precisión económica de Expresiones Regulares locales.
- **Búsqueda Flexible (Fuzzy)**: El algoritmo _thefuzz_ perdona errores tipográficos de los vendedores al buscar productos.
- **Staging Seguro**: Los datos dictados o subidos van a una bandeja temporal de revisión humana antes de inyectarse.
- **Arquitectura de Bodega (Data Warehouse)**: Separación clara entre capas `raw`, `staging` y `warehouse` para futuro Business Intelligence.
- **Frontend Interactivo**: Todo centralizado en una interfaz moderna de Streamlit de una sola página (SPA-like).

## 🏗️ Arquitectura

```text
┌─────────────────────────────────────────────────────────┐
│              Frontend e Interacciones (Streamlit)       │
│                  Carga Masiva | Dictado | CRUD          │
└────────────────────┬────────────────────────────────────┘
                     │ Interfaz
┌────────────────────▼────────────────────────────────────┐
│              Capa de Servicios Lógicos (Python)         │
│          db_service | extraction_service | state_mgr    │
├─────────────────────────────────────────────────────────┤
│  • Extracción NLP (Gemini) • Limpieza (Regex/Pandas)    │
│  • Resolución de Ambiguos  • Transacciones Atómicas     │
└────────────────────┬────────────────────────────────────┘
                     │ psycopg2
        ┌────────────┼────────────┐
        │                         │
   ┌────▼────┐               ┌────▼────┐
   │ BD RAW  │               │ BD W-H  │
   │ Crudos  │───────────────▶ Reportes│
   └─────────┘     ETL       └─────────┘
```

## 📁 Estructura del Proyecto

```text
proyecto-ventas/
├── imagen/                    # Recursos gráficos y logos
├── libs/                      # Bibliotecas utilitarias compartidas
│   ├── db_connection.py       # Gestor unificado PostgreSQL
│   ├── logger.py              # Centralización de logs de consola
│   └── models.py              # Definiciones compartidas
├── modules/                   # Módulos funcionales (Micro-arquitecturas)
│   └── ingesta_ventas/        # Core transaccional
│       ├── app.py             # Controlador principal
│       ├── README*.md         # Documentación de módulo
│       ├── components/        # Interfaces visuales exclusivas
│       │   ├── mass_upload.py # Lógica de Bulk Upload Excel
│       │   ├── voice_input.py # Dictado de ventas
│       │   ├── manual_input.py# Gestor de formulario
│       │   └── database_viewer.py # CRUD Interactivo (st.data_editor)
│       └── services/          # Lógica interna y comunicaciones
│           ├── db_service.py  # Conexiones, búsquedas e inserts 
│           ├── extraction_service.py # Gemini IA y Modelos Fallback
│           └── state_manager.py # Control de Buffers Temporales
├── pages/                     # Directorio de ruteo nativo de Streamlit
├── scripts/                   # Automatizaciones CLI (Clear DB, Mockers)
└── main.py                    # Punto de entrada y Landing Page
```

## 💻 Tecnologías Utilizadas

**Backend & Lógica:**
- Python 3.13: Lenguaje principal.
- psycopg2: Driver conector a la base de datos relacional.
- Pandas & NumPy: Manipulación, limpieza vectorial y cruces de datos (DataFrames).
- TheFuzz: Librería de coincidencia aproximada de cadenas (Fuzzy Matching).
- python-dotenv: Manejo seguro de credenciales (Aiven).

**Inteligencia Artificial:**
- Google Generative AI (Gemini 2.5 Flash): Extracción de entidades desde comandos de voz/texto suelto.

**Frontend:**
- Streamlit: Framework de Python para construir la web interactiva.

**Infraestructura:**
- PostgreSQL (Aiven Cloud): Base relacional centralizada.

## 🗄️ Base de Datos
El proyecto cuenta con un modelo dimensional (Estrella) implementando esquemas independientes:

- **Esquema `raw`**: Almacena el espejo transaccional exacto de las operaciones del usuario. Tablas base: `ventas_raw`, `inventario_raw`, `clientes_raw`.
- **Esquema `warehouse`**: Tablas consolidadas e identificadas para lectura inmediata por herramientas de Dashboarding. Tablas: `fact_ventas`, `dim_producto`, `dim_cliente`, `dim_fecha`.
