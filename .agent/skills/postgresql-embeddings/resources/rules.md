# Rules: PostgreSQL Embeddings (pgvector)

Reglas específicas para el desarrollo con embeddings en PostgreSQL.

## Configuración de Tabla
- **Dimensiones:** Siempre especificar dimensiones exactas: `vector(1536)`.
- **Integridad:** Considerar `NOT NULL` para columnas de embedding si son críticas para la búsqueda.

## Selección de Distancia
- **Cosine Distance (`<=>`):** Usar por defecto para embeddings de texto y modelos de lenguaje (RAG).
- **L2 Distance (`<->`):** Usar si el modelo fue entrenado específicamente para distancia Euclidiana.

## Estrategia de Indexado
- **HNSW (Recomendado):**
  - Usar para la mayoría de aplicaciones RAG.
  - Parámetros sugeridos: `m=16, ef_construction=64`.
  - Comando: `CREATE INDEX ON table USING hnsw (column vector_cosine_ops);`
- **IVFFlat:**
  - Usar solo si los recursos de memoria son extremadamente limitados o el tiempo de carga es crítico.
  - Requiere un dataset mínimo para entrenar las listas (`lists = round(sqrt(rows))`).

## Consultas y Performance
- **Limit:** Siempre incluir `LIMIT` en búsquedas vectoriales para evitar escaneos completos innecesarios.
- **Prefiltros:** Combinar filtros SQL normales (columnas de texto, fecha) con búsqueda vectorial para reducir el espacio de búsqueda.
