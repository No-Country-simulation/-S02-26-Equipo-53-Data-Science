---
name: Formulación de Preguntas
description: Estándar para la toma de requerimientos, clarificación de dudas y validación de flujos mediante preguntas rigurosas y visuales.
---

# Skill: Formulación de Preguntas

## Propósito
Asegurar que ninguna implementación compleja comience sin haber validado exhaustivamente los requerimientos ("Happy Path" y "Edge Cases"), visualizado la arquitectura y confirmado las asunciones del negocio.

## Cuándo Usar
- Antes de escribir código para una nueva funcionalidad compleja (ej. matrices dinámicas, flujos de pago, lógica de negocio core).
- Cuando el requerimiento del usuario sea ambiguo (ej. "mejora el sistema").
- Al detectar riesgos de incoherencia en los datos (ej. tipos de datos mixtos, ordenamientos extraños).

## Instrucciones

### 1. Casos Hipotéticos (Edge Cases)
No te limites a preguntar "¿cómo quieres esto?". Plantea escenarios futuros que podrían romper el sistema:
- **"¿Qué pasa si...?"**: Datos nulos, usuarios concurrentes, inputs inesperados.
- **Futuro vs. Presente**: "¿Esto debe funcionar solo para X o escalar a Y en el futuro?"
- **Contra-ejemplos**: "Si un usuario hace X, ¿el sistema debe bloquearlo o permitirlo?"

### 2. Visualización Obligatoria (Mermaid)
Siempre incluye un diagrama para confirmar tu entendimiento.
- Uss diagramas de flujo (`flowchart TD`) para lógica.
- Usa diagramas de secuencia (`sequenceDiagram`) para interacciones entre componentes.
- **Formato**:
    ```mermaid
    flowchart TD
    A[Usuario Input] -->|Valida| B{Es válido?}
    B -- Sí --> C[Procesar]
    B -- No --> D[Error]
    ```
- Acompaña el diagrama con: *"Así es como visualizo el flujo actual. ¿Es correcto?"*

### 3. Coherencia y Flujo
Cuestiona las brechas lógicas:
- "¿Cómo se conecta el componente A con el B si tienen formatos distintos?"
- "¿El paso 3 depende del paso 1 obligatoriamente?"

### 4. Confirmaciones Explícitas
Lista los componentes implicados y pide confirmación uno a uno si es necesario:
- [ ] Base de Datos (Schema)
- [ ] Frontend (UI/UX)
- [ ] Lógica de Negocio (Reglas)

### 5. Propuesta de Soluciones (Regla de 3 Opciones)
Nunca ofrezcas una única solución técnica ("La Solución"). Ofrece siempre un abanico de **3 opciones (A, B, C)** ordenadas por complejidad o enfoque.

**Fuente de las Opciones:**
1.  **Prioridad 1**: Búscalas en `resources/` del skill relevante.
2.  **Prioridad 2**: Si no hay recursos, usa tu conocimiento general de AI para proponer patrones estándar.

**Formato de Opciones:**
- **Opción A (Conservadora/Estándar)**: Lo más rápido/fácil/común.
- **Opción B (Robustez/Escalabilidad)**: Mejor arquitectura, más esfuerzo.
- **Opción C (Innovadora/Alternativa)**: Un enfoque diferente (ej. Serverless vs Monolito, CSS vs Tailwind).

**Iteración:**
- Si el usuario rechaza A, B y C, pregunta *por qué* y genera **otras 3 opciones** (D, E, F) basándote en el feedback.

## Estructura de la Pregunta

```markdown
### 1. Visualización del Flujo
[Diagrama Mermaid]
"Actualmente entiendo que el dato viaja de A a B..."

### 2. Casos Hipotéticos de Riesgo
- Caso A: Usuario ingresa talla "10" antes de "2". ¿Cómo ordenamos?
- Caso B: Producto nuevo sin categoría. ¿Se permite?

### 3. Propuesta de Implementación
He detectado estas formas de resolverlo:

| Opción | Descripción | Pro | Contra |
| :--- | :--- | :--- | :--- |
| **A** | Usar librería X | Rápido | Menos control |
| **B** | Custom implementation | Control total | Más código |
| **C** | Servicio externo Y | Delegado | Costo/Latencia |

¿Cuál prefieres?
```

## Logs
- LOG_INFO: "formulacion-preguntas: Generando cuestionario de validación para [tópico]..."
- LOG_INFO: "formulacion-preguntas: Diagrama de flujo creado para confirmación."
