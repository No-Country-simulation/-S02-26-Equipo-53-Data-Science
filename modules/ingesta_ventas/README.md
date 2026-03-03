# Módulo de Ingesta de Datos (Ventas e Inventario) 📊🎙️

Este módulo es el núcleo de entrada de la plataforma, encargado de la captura, procesamiento, validación y almacenamiento de los datos comerciales reales (Ventas e Inventario). 

Diseñado bajo la arquitectura modular de Streamlit local, consta de **tres modalidades de ingesta** orientadas a diferentes tipos de usuario (desde operaciones en tienda hasta administradores migrando datos heredados).

---

## 🚀 Estado Actual y Modalidades de Ingesta

El módulo se divide en 3 modalidades principales de captura, más una herramienta de administración interna.

### 1. 🎙️ Dictado y Extracción con IA (Completamente Funcional)
Diseñado para el **vendedor en tienda**, permite registrar ventas en segundos sin navegar por menús complejos.
- **Entrada Multimodal**: Permite grabar voz o escribir texto libre (Ej. _"Venta de 2 polos negros talla M a Carlos por yape"_).
- **Procesamiento de Lenguaje Natural**: Utiliza la API de **Gemini 2.5 Flash** para extraer todos los atributos (producto, cantidad, talla, color, precio especial, cliente, medio de pago).
- **Resolución Relacional ("Fuzzy Match")**: Tras la extracción IA, la base de datos busca coincidencias reales en el inventario actual de la Base de Datos.
- **Validación Humana (Data Editor)**: Muestra una grilla editable donde marca con ⚠️ conflictos de ambigüedad (Ej. múltiples variantes de polo negro) o datos faltantes. El insert a la DB (`raw.ventas_raw`) se bloquea hasta que el vendedor elige el ID correcto y las luces pasen a verde ✅.

### 2. 👆 Entrada Manual (En Desarrollo / Operativa)
Diseñada para registros tradicionales y metódicos.
- Funciona como el formulario estándar de la aplicación.
- Cuenta con selectores directos, campos controlados de autocompletado y validaciones puras.
- Ideal para cuando el entorno de la tienda es demasiado ruidoso para voz o cuando se requiere forzar campos específicos de creación sin recurrir al lenguaje natural.

### 3. 📂 Carga Inteligente por Lotes de Excel (Completamente Funcional)
Diseñado para la **migración inicial** y para analistas que traen historiales previos. Maneja dos ámbitos: **📦 Inventario Inicial** y **📈 Historial de Ventas**.
- **Mapeador Inteligente**: Si el usuario sube un CSV/Excel desordenado (no sigue la plantilla), Gemini IA entra como agente mapeador y sugiere cómo emparejar las columnas desconocidas hacia el modelo oficial relacional.
- **Extracción Híbrida (Limpieza Pandas + IA)**: Si en la carga se detectan descripciones largas que encapsulan los atributos (Ej. _"Zapatilla Running Azul Talla 42"_), Gemini detecta los Nulos de color/talla faltantes y destripa automágicamente la descripción base en las columnas correspondientes de talla y color, antes de insertarlo al backend.
- **Grid Predictiva**: Levanta todos los datos pre-procesados en la "Sala de Espera Humana", resaltando cualquier valor estrictamente obligatorio no suministrado de color rojo antes de ejecutar la resolución de bulk insert hacia el servidor PostgreSQL.

---

## 🛠️ Herramienta de Soporte
- **🔍 Consulta de Base de Datos**: Una pestaña extra para auditores que corre directamente comandos `SELECT` a la capa relacional para comprobar en vivo el éxito de los guardados y diagnosticar la estructura de las tablas `clientes_raw`, `inventario_raw` y `ventas_raw`.

---

## 🏗️ Flujo de Archivos Internos (Arquitectura)
1. `app.py`: El orquestador que gestiona las pestañas y los estados globales de la interfaz (incluyendo el Data Editor interactivo de resultados IA).
2. `components/voice_input.py`, `mass_upload.py`, `manual_input.py`: Las interfaces UI especializadas para cada modalidad.
3. `services/extraction_service.py`: Agente centralizadoizado en peticiones Gemini Prompting.
4. `services/db_service.py`: Puente relacional (`psycopg2`) y queries paramétricas. 

## ⚙️ Dependencias
Requiere de `streamlit`, entorno PostgreSQL (con permisos `GRANT INSERT, USAGE SEQUENCE`) activo, `pandas` para limpieza de datos matriciales, y el token de `GEMINI_API_KEY` correctamente declarado en el `.env`.
