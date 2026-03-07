# 🛠️ Guía de Desarrollo e Instalación

Instrucciones detalladas para configurar el entorno de desarrollo y contribuir al proyecto.

## 📋 Requisitos Previos
- Python 3.10+
- Acceso a una base de datos PostgreSQL (Aiven preferido).
- API Key de Google Gemini.

## 🛠️ Configuración Loclal
1. **Clonar**: `git clone [REPO_URL]`
2. **Entorno**: `python -m venv env`
3. **Activar**:
   - Win: `.\env\Scripts\activate`
   - Linux: `source env/bin/activate`
4. **Dependencias**: `pip install -r requirements.txt`
5. **Secretos**: Crear archivo `.env` basado en `.env.example`.

## 🧪 Comandos Útiles
- **Ejecutar App**: `streamlit run main.py`
- **Limpiar BD**: `python scripts/clear_aiven_db.py`
- **Poblar BD**: `python scripts/temp_old_db.py`

## 🚦 Flujo de Git
- Trabajar siempre sobre ramas de característica (`feature/nombre-de-la-mejora`).
- Realizar Pull Requests hacia la rama `develop2` para revisión.
