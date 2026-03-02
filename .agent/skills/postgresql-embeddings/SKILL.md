---
name: PostgreSQL Embeddings (pgvector)
description: Manejo de búsqueda vectorial y almacenamiento de embeddings en PostgreSQL usando pgvector
---

# Skill: PostgreSQL Embeddings

## Propósito
Integrar capacidades de base de datos vectorial en PostgreSQL para permitir búsquedas semánticas, recomendaciones y aplicaciones RAG de alta performance.

## Cuándo Usar
- Al diseñar sistemas que necesiten almacenar y comparar vectores de alta dimensión.
- Al implementar búsqueda semántica sobre documentos almacenados en Postgres.
- Cuando se necesite realizar búsquedas de similitud (K-NN) eficientes mediante índices ANN.

## Instrucciones

### 1. Habilitar la Extensión
Ejecutar en la base de datos:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Definición del Schema
Definir columnas con el tipo `vector` y dimensiones precisas:
```sql
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  content TEXT,
  embedding vector(1536) -- Dimensiones de OpenAI text-embedding-3-small
);
```

### 3. Operaciones de Búsqueda
Utilizar los operadores de distancia según el caso de uso:
- **Cosine Distance (`<=>`):** Recomendado para RAG y texto.
- **Euclidean Distance (`<->`):** Para distancias geométricas directas.

```sql
SELECT content FROM documents 
ORDER BY embedding <=> '[...vector...]' 
LIMIT 5;
```

### 4. Índices para Performance
Para grandes volúmenes de datos, crear índices HNSW:
```sql
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
```

## Ejemplos
Ver carpeta `examples/ejemplo_basico.md`.

## Resources
Ver carpeta `resources/rules.md` para mejores prácticas de indexing.

## Logs
- LOG_INFO: "postgresql-embeddings: Extensión verificada/habilitada"
- LOG_INFO: "postgresql-embeddings: Búsqueda vectorial ejecutada (métrica: [distancia])"
- LOG_WARN: "postgresql-embeddings: No se encontró índice eficiente para la columna vectorial"
