# 📔 Portal de Documentación Técnica - DATAMARK

<p align="center">
  <img src="https://img.shields.io/badge/Status-Estable-success?style=for-the-badge&logo=checkbox" alt="Status">
  <img src="https://img.shields.io/badge/Arquitectura-Modular-blue?style=for-the-badge&logo=docker" alt="Arquitectura">
  <img src="https://img.shields.io/badge/Motor_IA-Gemini_Flash-orange?style=for-the-badge&logo=google-cloud" alt="IA">
  <img src="https://img.shields.io/badge/Base_de_Datos-Aiven_PostgreSQL-red?style=for-the-badge&logo=postgresql" alt="DB">
</p>

---

## 🌟 Introducción
Bienvenido al cerebro de **DATAMARK**. Este repositorio de documentación ha sido diseñado para proporcionar una "estabilidad máxima" en la comprensión del proyecto. No se trata solo de manuales, sino de una hoja de ruta técnica completa que explica cómo transformamos la incertidumbre del lenguaje natural en datos accionables para negocios reales.

> [!TIP]
> Esta documentación utiliza diagramas dinámicos de **Mermaid**. Si no se visualizan correctamente, asegúrate de usar un visor compatible con GFM (GitHub Flavored Markdown).

---

## 🎯 Objetivos de la Plataforma
La misión de DATAMARK se resume en cuatro pilares fundamentales:

1.  **Fricción Cero**: Permitir que cualquier dueño de negocio ingrese datos sin necesidad de teclados, solo con su voz.
2.  **Integridad Absoluta**: Garantizar que cada transacción impacte de forma correcta y segura en el inventario real.
3.  **Inteligencia Adaptativa**: Utilizar LLMs para entender el contexto y corregir errores humanos de forma proactiva.
4.  **Escalabilidad en la Nube**: Mantener una infraestructura robusta capaz de crecer junto al negocio.

---

## 🏗️ Mapa de Arquitectura General
A continuación, se presenta la visión holística de la orquestación del sistema:

```mermaid
graph LR
    subgraph "Entrada Multimodal"
        A[Dictado por Voz]
        B[Carga Excel/CSV]
        C[Formuario Manual]
    end

    subgraph "Capa de Inteligencia"
        D{Orquestador AI}
        E[Gemini API]
        F[Fuzzy Filter]
    end

    subgraph "Capa de Datos"
        G[(RAW Layer)]
        H((ETL Process))
        I[(Warehouse Layer)]
    end

    subgraph "Consumo"
        J[Reporting BI]
        K[CRUD Admin]
    end

    A & B & C --> D
    D <--> E
    D --> F
    F --> G
    G --> H
    H --> I
    I --> J
    G <--> K
```

---

## 📂 Recursos de Profundización
Haz click en los enlaces para explorar los detalles técnicos de cada componente:

| Módulo | Descripción Técnica | Documento |
| :--- | :--- | :--- |
| **Arquitectura** | Detalle de capas, diagramas de secuencia e infraestructura. | [Ver más ➔](arquitectura.md) |
| **Ingeniería de Datos** | Modelado Star Schema, disparadores PL/pgSQL y esquemas. | [Ver más ➔](base_de_datos.md) |
| **Inteligencia Artificial** | Prompt engineering, fallback de modelos y lógica NLP. | [Ver más ➔](ia_nlp.md) |
| **Funcionalidades** | Desglose de submódulos de ingesta, auditoría y BI. | [Ver más ➔](funcionalidades.md) |
| **Guía de Desarrollo** | Setup de entorno, DevOps y Troubleshooting. | [Ver más ➔](guia_desarrollo.md) |

---

## 🛠️ Setup Operativo (Quick Start)
Para poner en marcha la infraestructura de documentación y desarrollo:

1.  **Variables de Entorno**: Asegúrate de tener configurado tu `.env` con las credenciales de Aiven y Gemini.
2.  **Base de Datos**: Ejecuta el script `db_model.sql` para inicializar los esquemas `raw`, `staging` y `warehouse`.
3.  **Servidor**: Inicia el orquestador con `streamlit run main.py`.

> [!IMPORTANT]
> Para contribuciones relacionadas con la documentación, por favor mantén el estándar de Mermaid y utiliza las etiquetas de alerta (`NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION`) para resaltar información crítica.

---

## 🎨 Características de Diseño
- **Modularidad**: Cada archivo `.md` es independiente pero está interconectado.
- **Visualización**: Priorizamos diagramas sobre bloques de texto extensos.
- **Consistencia**: Uso de nomenclatura técnica en inglés para código y español para explicaciones.

---
<p align="center">
  Hecho con ❤️ por el equipo de DATAMARK
</p>
