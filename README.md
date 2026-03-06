# DATAMARK - Plataforma Analítica y Transaccional Automatizada

## 🏆 Insignias
![Python](https://img.shields.io/badge/Python-3.13-3776ab?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791?style=flat-square&logo=postgresql&logoColor=white)
![Aiven](https://img.shields.io/badge/Aiven-Managed_DB-ff3366?style=flat-square&logo=aiven&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-Streamlit_Community_Cloud-FF4B4B?style=flat-square&logo=streamlit)
![Status](https://img.shields.io/badge/Status-Production-brightgreen?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0-blue?style=flat-square)

## 📌 Índice
- [Descripción](#-descripción)
- [Roles del Proyecto](#-roles-del-proyecto)
- [Funciones y Aplicaciones](#-funciones-y-aplicaciones)
- [Arquitectura Modular](#-arquitectura-modular)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Base de Datos (Aiven PostgreSQL)](#-base-de-datos-aiven-postgresql)
- [Despliegue (Streamlit Cloud)](#-despliegue-streamlit-cloud)
- [Instalación y Contribución](#-instalación-y-contribución)

## 📙 Descripción
**DATAMARK** es una plataforma integral diseñada para pequeños y medianos negocios (retail, calzado, ropa) en provincias del Perú. Actúa como un *Data Analyst Automatizado*, combinando la facilidad de **Streamlit** para la ingesta de datos con NLP (Lenguaje Natural) y la solidez de **PostgreSQL** alojado en la nube de **Aiven**. Transforma la captura de ventas diarias y la gestión de inventario en reportes y dashboards dinámicos para la toma de decisiones.

## 👥 Roles del Proyecto
El desarrollo se dividió en roles especializados para asegurar calidad y modularidad:
- **Implementador (Core & Backend)**: Creación de la arquitectura base, flujos transaccionales (CRUD), validaciones lógicas y conexiones seguras con la base de datos (`libs.db_connection`, Psycopg2 y SQL puro sin abstracciones innecesarias).
- **Especialista AI (NLP)**: Integración de los modelos Gemini Flash para permitir la inyección de datos a través de inteligencia artificial (dictados de voz y deducción de atributos faltantes).
- **Frontend / Data Viz**: Diseño de la SPA en el Framework de Streamlit, incluyendo el Landing Page y las gráficas analíticas interactivas.

## 🎥 Funciones y Aplicaciones
- **Ingesta Inteligente**: Registro de ventas mediante voz (dictado natural), carga masiva (Excel/CSV) o ingreso manual, con NLP y expresiones regulares deterministas.
- **Gestión CRUD Integrada**: Edición visual directa (`st.data_editor`) sobre las tablas transaccionales de la base de datos de manera paginada.
- **Dashboarding Dinámico**: Tableros analíticos creados en tiempo real leyendo directamente del Data Warehouse.
- **Validación Estricta**: Sistema anti-caídas que revisa relaciones físicas (Stock suficiente, Cliente existente) antes de impactar en la capa transaccional.

## 🏗️ Arquitectura Modular

```text
┌─────────────────────────────────────────────────────────┐
│              Capa de Presentación (Streamlit Framework) │
│                main.py | pages/ | UI Components         │
└────────────────────┬────────────────────────────────────┘
                     │ Llamadas asíncronas / Interfaz
┌────────────────────▼────────────────────────────────────┐
│              Capa de Negocio Lógica (Modules)           │
│         ingesta_ventas | analisis | dashboard | libs    │
├─────────────────────────────────────────────────────────┤
│  • Extracción NLP (Gemini) • Limpieza Data (Pandas)     │
│  • Conexiones Centralizadas • Fuzzy Matching / Regex    │
└────────────────────┬────────────────────────────────────┘
                     │ Psycopg2
┌────────────────────▼────────────────────────────────────┐
│              Capa de Datos Cloud (Aiven PostgreSQL)     │
│              Esquemas: raw → staging → warehouse        │
└─────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```text
proyecto-de-proyectos/
├── imagen/                    # Recursos visuales
├── libs/                      # Bibliotecas técnicas compartidas
│   ├── db_connection.py       # Gestor unificado para Aiven PostgreSQL
│   ├── logger.py              # Centralización de consola
│   └── models.py              # Modelos base
├── modules/                   # Módulos Funcionales Aislados
│   ├── analisis/              # Procesos de Data Science
│   ├── dashboard/             # Motor de BI visual
│   ├── gestion_dueño/         # Panel administrativo
│   └── ingesta_ventas/        # Core transaccional y NLP
├── pages/                     # Wrappers nativos de Streamlit para el menú
├── scripts/                   # Automatizaciones (Mockers y Clear DB)
├── main.py                    # Landing Page Inicial
├── requirements.txt           # Dependencias exactas
└── README.md                  # Este documento
```

## 💻 Tecnologías Utilizadas
- **Core de Programación**: Python 3.10+
- **Framework Frontend**: [Streamlit](https://streamlit.io/) (Despliegue Web Rápido y Análisis).
- **Procesamiento de Datos**: Pandas, NumPy, TheFuzz (Regex y coincidencia aproximada).
- **Inteligencia Artificial**: Google Gemini API (2.5 Flash).
- **Control de Bases de Datos**: `psycopg2` puro.

## 🗄️ Base de Datos (Aiven PostgreSQL)
**DATAMARK** se enorgullece de usar **[Aiven for PostgreSQL](https://aiven.io/)** como su base de datos principal, garantizando alta disponibilidad, seguridad y resiliencia en la nube. 
El diseño utiliza arquitectura por esquemas:
- **`raw`**: Recepción transaccional inmediata (OLTP). Tablas: `ventas_raw`, `inventario_raw`, `clientes_raw`.
- **`warehouse`**: Capa dimensional limpia para Business Intelligence (OLAP) con Dimensiones y Hechos listos.

## ☁️ Despliegue (Streamlit Cloud)
El proyecto ha sido concebido para ser hosteado bajo *Streamlit Community Cloud*. Toda la configuración ambiental dependiente (Aiven DB Hosts, Passwords, Gemini API Key) está estructurada para cargarse de forma segura a través de los *Streamlit Secrets* (`.streamlit/secrets.toml` o variables de entorno), independizando el código fuente de los datos sensibles y facilitando integraciones continuas (CI/CD).

## 🚀 Instalación y Contribución

### 1. Requisitos Previos
- Python 3.10 o superior ([Descargar aquí](https://www.python.org/downloads/)).
- Git ([Descargar aquí](https://git-scm.com/)).

### 2. Clonar y Preparar el Entorno
```bash
# 1. Clona el repositorio
git clone https://github.com/No-Country-simulation/-S02-26-Equipo-53-Data-Science.git
cd -S02-26-Equipo-53-Data-Science

# 2. Crea un entorno virtual
python -m venv env

# 3. Activa el entorno
# En Windows:
env\Scripts\activate
# En Linux/Mac:
source env/bin/activate

# 4. Instala las dependencias
pip install -r requirements.txt
```

### 3. Configuración del Módulo
Copia el archivo base de variables y llena tus credenciales (Aiven PostgreSQL / Gemini):
```bash
cp .env.example .env
```

### 4. Ejecución del Proyecto
Inicia el servidor local de Streamlit:
```bash
streamlit run main.py
```

### 5. Flujo de Trabajo (Git Flow)
1. Haz un fork y asegurate de trabajar en tu máquina local en la rama adecuada (ej: `develop2`).
2. Haz check-out para tu feature: `git checkout -b <nombre-del-aporte>`
3. Empuja a tu repositorio: `git push origin HEAD`
4. Crea un **Pull Request** detallando tus adiciones funcionales.
