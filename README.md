# GB Bot WhatsApp - Asistente de Inteligencia Artificial

Solución corporativa de atención automatizada y gestión de leads para **GB Soluciones Digitales**. Este sistema actúa como un webhook de alta disponibilidad capaz de interceptar mensajes de la API de WhatsApp Cloud (Meta), procesar las intenciones de los clientes utilizando modelos generativos avanzados de OpenAI (GPT-4o-mini) y consultar dinámicamente el catálogo de servicios técnicos de la consultora.

La arquitectura está diseñada bajo principios de software robustos, desacoplados y preparados para entornos de producción en la nube.

---

## 🛠️ Stack Tecnológico

- **Core Backend:** FastAPI (Python 3.11+) - Framework asíncrono de alto rendimiento.
- **Servidor ASGI:** Uvicorn - Manejo eficiente de concurrencia y peticiones en tiempo real.
- **Motor de IA:** OpenAI API (GPT-4o-mini) - Procesamiento del lenguaje natural y análisis de intenciones.
- **Cliente HTTP Asíncrono:** HTTPX - Comunicación fluida con los endpoints de Meta Graph API.
- **Infraestructura y Despliegue:** Railway Pro (PaaS) con soporte para contenedores y variables de entorno cifradas.
- **Automatización CI/CD:** GitHub Actions - Canalización de integración continua para validar la integridad del código antes de producción.

---

## 📂 Estructura del Proyecto

```text
gb_bot_whatsapp/
├── .github/
│   └── workflows/
│       └── main.yml
├── public/
│   └── index.html
├── src/
│   ├── __init__.py
│   ├── bot_logic.py
│   ├── main.py
│   └── services/
│       ├── __init__.py
│       ├── data_servicios.json
│       └── servicio_manager.py
├── .gitignore
├── .env
├── README.md
└── requirements.txt
```

---

## 🛠 Instalación local
1. Clonar el repo: `git clone https://github.com/Brian13b/bot_gb_soluciones_digitales.git`
2. Crear entorno: `python -m venv .venv`
3. Activar entorno: `.\.venv\Scripts\Activate.ps1`
4. Activar y subir dependencias: `pip install -r requirements.txt`
5. Definición de Variables de Entorno
6. Ejecutar: `uvicorn src.main:app --reload`

---

## 🗺️ Roadmap de Desarrollo

El proyecto se encuentra estructurado en fases incrementales para asegurar la estabilidad y el escalamiento óptimo de la plataforma:

### 🟩 Fase 1: Arquitectura Núcleo e Infraestructura Local (Completado)
* Definición de la estructura modular del proyecto.
* Configuración de FastAPI y endpoints de simulación asíncrona.
* Creación del `ServicioManager` utilizando algoritmos de coincidencia de texto locales (`difflib`) para pruebas seguras con cero costo de API.
* Creación de una interfaz gráfica mínima (`public/index.html`) para pruebas de caja negra del backend.

### 🟨 Fase 2: Despliegue en la Nube y CI/CD (Completado)
* Configuración del repositorio remoto en GitHub y resolución de conflictos de ramas iniciales.
* Despliegue automatizado en Railway Pro conectando el pipeline de GitHub Actions.
* Exposición del puerto dinámico mediante la inyección del comando `Procfile` y la variable `$PORT`.

### 🟦 Fase 3: Conexión de API Externa e Inteligencia Generativa (Actual)
* Habilitación de la cuenta de facturación en OpenAI e integración del SDK oficial con el modelo `gpt-4o-mini`.
* Superación de los factores de validación de Meta for Developers para adquirir el `PHONE_NUMBER_ID` de desarrollo.
* Refactorización de `src/main.py` para parsear la estructura anidada de los objetos JSON reales enviados por WhatsApp Cloud API.

### 🚀 Fase 4: Persistencia de Datos y Gestión de Contexto (Proximo)
* Integración de una base de datos relacional (PostgreSQL en Railway) mediante un ORM como SQLAlchemy.
* Implementación de un sistema de gestión de estados conversacionales (*Conversation State Management*) para que la IA recuerde el contexto histórico de los mensajes previos de cada cliente (basado en el número de teléfono).

### 🎨 Fase 5: Panel de Control Administrativo (Dashboard)
* Desarrollo de un Frontend robusto y exclusivo para la administración de **GB Soluciones Digitales**.
* **Identidad Visual:** Diseño de la interfaz enfocado en un enfoque corporativo y limpio utilizando una paleta de colores sofisticada en tonos naranja y arena.
* **Funcionalidades Clave:**
  * Monitoreo en tiempo real de chats activos.
  * Métricas avanzadas de conversión (consultas que se convirtieron en propuestas de proyectos).
  * **Mecanismo de Traspaso Humano (Human-in-the-Loop):** Permite que un desarrollador del equipo tome el control manual de la conversación de WhatsApp directamente desde el panel si el cliente solicita un requerimiento altamente específico o una cotización manual compleja.