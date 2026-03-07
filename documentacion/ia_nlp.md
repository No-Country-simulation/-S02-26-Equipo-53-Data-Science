# 🎙️ IA y Procesamiento de Lenguaje Natural

El corazón de DATAMARK es su capacidad para entender y procesar entradas de datos no estructuradas de forma inteligente.

## 🤖 Integración con Google Gemini
Utilizamos el modelo **Gemini 2.5 Flash** para:
- **Parsear Dictados**: Extraer variables (producto, cantidad, precio, cliente) de oraciones naturales.
- **Inferencia de Atributos**: Deducir información faltante basándose en el contexto.
- **Estructuración**: Convertir audio/texto en objetos JSON listos para validación.

## 🔍 Algoritmos de Coincidencia (Fuzzy Matching)
Para evitar la duplicidad de datos por errores tipográficos o variaciones en el nombre del producto:
1. **Levenshtein Distance**: Aplicamos el algoritmo `Token Sort Ratio` de la librería `TheFuzz`.
2. **Validación Determinista**: Limpieza previa con expresiones regulares para tallas y colores.

## ⚙️ Flujo de Refinamiento
1. Entrada de voz -> Transcripción.
2. Transcripción -> Extracción AI (Gemini).
3. JSON Extraído -> Cruce con Base de Datos (Fuzzy Matching).
4. Confirmación del Usuario -> Inserción en BD.
