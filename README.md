# GB Bot WhatsApp - Asistente IA

Bot de atención automatizada para **GB Soluciones Digitales**. Desarrollado con FastAPI y diseñado para integrar inteligencia artificial en la gestión de servicios digitales.

## 🚀 Características
- **Backend Robusto:** FastAPI para procesamiento de webhooks.
- **Lógica Inteligente:** Sistema modular basado en `ServicioManager` para consultas rápidas.
- **Preparado para IA:** Arquitectura lista para integrar OpenAI GPT-4o.
- **Despliegue Profesional:** Automatizado vía GitHub Actions y Railway.

## 🛠 Instalación local
1. Clonar el repo: `git clone`
2. Crear entorno: `python -m venv .venv`
3. Activar y subir dependencias: `pip install -r requirements.txt`
4. Ejecutar: `uvicorn src.main:app --reload`