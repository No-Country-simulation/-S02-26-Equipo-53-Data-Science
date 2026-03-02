---
trigger: always_on
---

# Regla: Preguntar Rigurosamente

**Propósito**: Evitar asunciones y simplificaciones excesivas en tareas complejas.

## Instrucción
Antes de proponer o ejecutar una implementación técnica compleja (arquitectura, lógica de negocio, flujos de datos), **SIEMPRE** debes usar el skill `formulacion-preguntas`.

1.  **No asumas**: Si el usuario pide "una matriz", no asumas que es una tabla simple. Cuestiona los bordes.
2.  **Visualiza**: Genera un diagrama Mermaid para confirmar que tu mapa mental coincide con el del usuario.
3.  **Casos Hipotéticos**: Propón escenarios de fallo o futuro (scalability) para validar robustez.
4.  **Ofrece Opciones (A/B/C)**: Presenta siempre 3 caminos para implementar la solución (Conservador, Robusto, Alternativo). Si se rechazan, itera.

## Excepciones
- Tareas triviales (corregir un typo, cambiar un color).
- Cuando el usuario explícitamente pide "algo rápido y sucio" (quick & dirty).
