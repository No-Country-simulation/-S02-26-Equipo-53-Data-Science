# Ejemplo: Búsqueda Semántica de Documentos

## Contexto
Este ejemplo muestra cómo crear un sistema básico de búsqueda semántica donde almacenamos fragmentos de texto con sus correspondientes embeddings generados por un modelo de IA (como OpenAI o Gemini).

## Entrada
El usuario necesita buscar documentos similares a una consulta dada.
- Tabla: `knowledge_base`
- Consulta vectorial: `[0.012, -0.023, 0.045, ...]` (1536 dimensiones)

## Proceso

### 1. Preparación de la DB
```sql
-- Activar extensión
CREATE EXTENSION IF NOT EXISTS vector;

-- Crear tabla con dimensiones específicas
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    body TEXT,
    embedding vector(1536)
);

-- Crear índice para búsqueda rápida
CREATE INDEX ON knowledge_base USING hnsw (embedding vector_cosine_ops);
```

### 2. Inserción de Datos
```sql
INSERT INTO knowledge_base (title, body, embedding) 
VALUES ('Configuración de Postgres', 'Guía paso a paso sobre Postgres...', '[0.012, -0.023, ...]');
```

### 3. Ejecución de Búsqueda
```sql
-- Buscar los 3 documentos más relevantes usando distancia coseno
SELECT title, body, 1 - (embedding <=> '[...query_vector...]') as similarity
FROM knowledge_base
ORDER BY embedding <=> '[...query_vector...]'
LIMIT 3;
```

## Salida Esperada
Una lista de registros ordenados por similitud, donde los resultados más cercanos a la consulta semántica aparecen primero.
- `title`: Configuración de Postgres
- `similarity`: 0.942
