# 🏗️ Arquitectura de la Solución

![Capa-Frontend](https://img.shields.io/badge/Capa-Frontend-FF4B4B?style=flat-square&logo=streamlit)
![Capa-Backend](https://img.shields.io/badge/Capa-Backend-3776ab?style=flat-square&logo=python)
![Capa-Cómputo](https://img.shields.io/badge/Capa-Cómputo-4285F4?style=flat-square&logo=google-cloud)


## 🗺️ Introducción Arquitectónica
La arquitectura de DATAMARK se basa en la **Separación de Responsabilidades (SoC)**. Hemos diseñado un sistema donde el flujo de información es unidireccional y predecible, minimizando los efectos secundarios en la base de datos transaccional.

---

## 📐 Topología de Capas
El sistema opera sobre una infraestructura 100% cloud:
1.  **Presentación**: Streamlit Community Cloud (Frontend reactivo).
2.  **Cómputo**: Python Business Logic + Google Gemini API (NLP).
3.  **Persistencia**: Aiven PostgreSQL Managed (Storage & ETL).

---

## 🔄 Estados del Sistema
El orquestador gestiona el ciclo de vida mediante los siguientes estados:

*   **[Inactivo]** ➔ Usuario presiona 'Grabar'
*   **[Escuchando]** ➔ Captura de buffer ➔ **[Procesando]**
*   **[Procesando]** ➔ Gemini API Extract ➔ **[Validando]**
*   **[Validando]** ➔ Fuzzy Match de productos ➔ **[Confirmación]**
*   **[Confirmación]** ➔ Aprobación de usuario ➔ **[Inserción]**
*   **[Inserción]** ➔ SQL Execute ➔ **[Finalizado]**

*En caso de fallo en cualquier punto, el sistema retorna a **[Inactivo]** con una notificación de error.*

---

## 🔧 Componentes de Software

### 1. Orquestador de Módulos
Localizado en `modules/[nombre_modulo]/app.py`. Es el encargado de inicializar los componentes de UI y llamar a los servicios de backend correspondientes.

### 2. Capa de Servicios
Contiene la lógica pesada de interacción externa:
- **`db_service.py`**: Adaptadores SQL y validaciones deterministas.
- **`extraction_service.py`**: Interfaz con el LLM y lógica de reintentos.

### 3. Shared Libs (`libs/`)
- **`db_connection.py`**: Implementa el patrón Singleton para asegurar una única gestión del pool de conexiones a Aiven.
- **`logger.py`**: Sistema de trazas jerárquico para auditoría en tiempo real.

---

## 🧪 Estrategia de Estabilidad
Para garantizar la máxima disponibilidad, implementamos:
- **Fallback de Modelos**: Descenso gradual de Gemini 3.1 -> 1.5 si se detectan cuotas excedidas.
- **Circuit Breaker**: Si la base de datos no responde, la aplicación entra en modo 'Solo Lectura' sobre el caché local de sesión.

---
> [!TIP]
> Puedes encontrar más detalles sobre el comportamiento de la IA en la sección [Inteligencia Artificial](ia_nlp.md).
