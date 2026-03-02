---
name: Automatización Tech
description: Especialista en principios de automatización y herramientas basadas en Python
---

# Skill: Automatización Tech

## Propósito
Este skill proporciona los principios, estrategias de escalado y conocimientos técnicos necesarios para implementar soluciones de automatización eficientes, con un enfoque especial en el ecosistema de Python.

## Cuándo Usar
- Al diseñar flujos de trabajo automatizados (web, desktop, datos).
- Al elegir herramientas para pruebas automatizadas o RPA.
- Al planificar el escalado de procesos manuales a sistemas automatizados.
- Al implementar bots de scraping o integraciones con LLMs (LangChain).

## Instrucciones

### 1. Aplicar Principios de Automatización
- **Simplifica primero:** Antes de automatizar, analiza si el proceso puede ser simplificado o eliminado.
- **Busca la precisión:** Define una fuente única de verdad para los datos que usará la automatización.
- **Diseña para el fallo:** Implementa logs detallados (utilizando `src/utils/logger.js`) y manejo de errores simple pero efectivo.

### 2. Selección de Herramientas (Python Focus)
- **Web Testing/Scraping:** Prefiere `Playwright` por su velocidad o `BeautifulSoup` para contenido estático.
- **RPA:** Usa `PyAutoGUI` para tareas de interfaz de usuario simples.
- **Datos:** Usa `Pandas` para procesar grandes volúmenes de información de forma automatizada.
- **IA/LLMs:** Usa `LangChain` o `smolagents` para flujos que requieran razonamiento.

### 3. Estrategia de Escalado
- Empieza con scripts independientes enfocados en tareas específicas.
- Evoluciona hacia orquestadores (Airflow) o integradores (n8n) para conectar procesos.
- Mantén la independencia tecnológica mediante APIs y formatos de datos estándar (JSON, CSV).

## Ejemplos
Ver carpeta `examples/` para casos de uso específicos.

## Resources
- `resources/knowledge-source.md`: Documentación completa de principios y tecnologías.
- `resources/rules.md`: Reglas específicas para el desarrollo de automatizaciones.

## Logs
- LOG_INFO: "automation-tech: Ejecutando flujo de [nombre-proceso]..."
- LOG_SEQUENCE: "Iniciando paso [n] de la secuencia de automatización..."
- LOG_ERROR: "Fallo en la automatización: [detalle]"
