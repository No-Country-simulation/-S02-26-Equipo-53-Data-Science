# 🏗️ Arquitectura de la Solución

DATAMARK implementa una arquitectura desacoplada basada en el principio de separación de responsabilidades (SoC), utilizando Python como orquestador central.

## 📐 Vista de Alto Nivel

```mermaid
graph TB
    subgraph Cliente ["Capa de Presentación (Streamlit)"]
        Landing["Landing Page"]
        Ingesta["Módulo de Ingesta"]
        Dash["Dashboard BI"]
    end

    subgraph Logica ["Capa de Aplicación (Python)"]
        Orq["Orquestador de Módulos"]
        AI["Motor NLP (Gemini)"]
        Fuzzy["Motor de Match (TheFuzz)"]
        Valid["Validación de Negocio"]
    end

    subgraph Persistencia ["Capa de Datos (PostgreSQL)"]
        RawDB[("Esquema RAW (OLTP)")]
        StgDB[("Esquema Staging")]
        WhDB[("Esquema Warehouse (OLAP)")]
    end

    Cliente <--> Logica
    Logica <--> Persistencia
```

## 🔄 Ciclo de Vida de una Venta

El proceso desde que el usuario dicta una venta hasta que aparece en el dashboard analítico:

```mermaid
sequenceDiagram
    participant U as Usuario
    participant S as Streamlit (UI)
    participant G as Gemini API
    participant P as PostgreSQL (Raw)
    participant W as PostgreSQL (WH)

    U->>S: Dicta: "Vendí 2 casacas azules"
    S->>G: Envía audio/texto
    G-->>S: Retorna JSON estructurado
    S->>P: Validación de stock (Trigger)
    alt Stock Suficiente
        P-->>S: Confirmación de venta
        S->>U: Notifica "Venta Exitosa"
    else Stock Insuficiente
        P-->>S: Error de integridad
        S->>U: Notifica "Error: Sin Stock"
    end
    Note over P,W: Proceso ETL (Diferido)
    P->>W: Migración a Fact_Ventas
```

## 🛠️ Stack Tecnológico Interno

- **Frontend**: Streamlit 1.40+ con componentes personalizados para grabación de audio.
- **Backend**: Python 3.10+ utilizando `psycopg2` para interactuar con la base de datos de manera determinista.
- **IA**: Modelos Gemini (Flash 1.5, 2.5, 3.1) con sistema de fallback automático.
- **Data**: Aiven PostgreSQL 16 con aislamiento de esquemas.
