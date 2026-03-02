# Knowledge Source: pgvector (PostgreSQL Embeddings)

- **Source URL:** https://github.com/pgvector/pgvector
- **Date Captured:** 2026-02-10
- **Summary:** Open-source vector similarity search for PostgreSQL.

## Core Concepts

### Installation & Setup
- `CREATE EXTENSION vector;` - Enable the extension.
- `vector(N)` - New data type for N-dimensional vectors.

### Comparison Operators
- `<->` - Euclidean (L2) distance
- `<#>` - Negative inner product
- `<=>` - Cosine distance
- `<+>` - Manhattan distance

### Indexing
- **HNSW:** Better query performance, higher build time/memory. Best for high accuracy.
- **IVFFlat:** Faster build time, lower memory. Good for very large datasets if HNSW is too heavy.

### Queries
```sql
-- Get top 5 nearest neighbors by L2 distance
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

-- Get neighbors within a certain distance
SELECT * FROM items WHERE embedding <-> '[3,1,2]' < 0.5;
```

### Best Practices
- Use `halfvec` for storage efficiency if precision loss is acceptable.
- Indexing with `HNSW` is generally recommended for most LLM/Embedding use cases.
- Match dimensions exactly (e.g., 1536 for OpenAI `text-embedding-3-small`).
