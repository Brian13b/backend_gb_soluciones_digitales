# GB Bot WhatsApp - Asistente de Inteligencia Artificial

Solución corporativa de atención automatizada y calificación de leads para **GB Soluciones Digitales**. Este sistema actúa como un webhook de alta disponibilidad capaz de interceptar mensajes de la API de WhatsApp Cloud (Meta), clasificar intenciones de clientes utilizando modelos generativos avanzados de OpenAI (GPT-4o-mini) mediante una arquitectura **stateless sin loops**, y derivar leads calificados de forma inmediata.

**Filosofía del Bot**: No es un vendedor, sino un **pre-filtro técnico inteligente**. Entiende en qué estado está el cliente (exploración vs. necesidad específica) y actúa en consecuencia. Su objetivo es capturar el problema del usuario con una sola pregunta estratégica y derivar al equipo humano para la venta real.

La arquitectura está diseñada bajo principios de software robustos, desacoplados y preparados para entornos de producción en la nube. **Listo para escalar a múltiples canales y integraciones futuras.**

---

## 🛠️ Stack Tecnológico

### Core Actual
- **Backend:** FastAPI (Python 3.11+) - Framework asíncrono de alto rendimiento.
- **Servidor ASGI:** Uvicorn - Manejo eficiente de concurrencia y peticiones en tiempo real.
- **Motor de IA:** OpenAI API (GPT-4o-mini) - Clasificación de intenciones sin loops (State Routing).
- **Cliente HTTP:** HTTPX - Comunicación fluida con Meta Graph API y OpenAI.
- **Despliegue:** Railway Pro (PaaS) con variables de entorno cifradas.
- **CI/CD:** GitHub Actions - Validación automática antes de producción.

### Stack Futuro (Opcional)
- **Database:** PostgreSQL en Railway + SQLAlchemy ORM
- **Frontend Widget:** React + TypeScript (iframe embebible en web)
- **Dashboard Admin:** React.js + Tailwind CSS
- **Notificaciones:** Discord.py, SendGrid, Slack SDK
- **Analytics:** Custom dashboards con PostgreSQL + Chart.js

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
├── requirements.txt
└── (En futuro)
    ├── database/
    │   └── models.py (SQLAlchemy)
    ├── dashboard/
    │   └── (React.js app)
    ├── widget/
    │   └── (React component)
    └── migrations/
        └── (Alembic)
```

---

## 🏗️ Arquitectura del Sistema

### Flujo Actual (Fase 3.5)
```
Cliente en WhatsApp
        ↓
   Pregunta al Bot
        ↓
  OpenAI (GPT-4o-mini)
  State Routing:
  - ESTADO A (Exploración) → Asesor breve + 1 pregunta
  - ESTADO B (Captura) → Derivación inmediata al equipo
        ↓
  Respuesta al cliente
        ↓
 [FIN - Sin almacenamiento ni historial centralizado]
```

### Flujo Futuro Recomendado (Opcional - Fase 4+)
```
Cliente en Web (Widget) o WhatsApp
        ↓
  OpenAI (GPT-4o-mini)
        ↓
  PostgreSQL (Guardar conversación + score)
        ↓
  [Si ESTADO B → Notificación a ti]
        ↓
  Dashboard Admin (Ver lead)
        ↓
  Abre en WhatsApp desde Dashboard
        ↓
  Responde directamente
        ↓
  Almacenado en DB + Analytics
```

---

## 🛠 Instalación local
1. Clonar el repo: `git clone https://github.com/Brian13b/bot_gb_soluciones_digitales.git`
2. Crear entorno: `python -m venv .venv`
3. Activar entorno: `.\.venv\Scripts\Activate.ps1`
4. Instalar dependencias: `pip install -r requirements.txt`
5. Crear archivo `.env` con variables requeridas (ver sección Variables de Entorno abajo)
6. Ejecutar: `uvicorn src.main:app --reload`

### Variables de Entorno Requeridas
```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# WhatsApp / Meta
WHATSAPP_TOKEN=your-token-here
VERIFY_TOKEN=your-verify-token-here
PHONE_NUMBER_ID=your-phone-id-here
```

### Pruebas Locales
```bash
# Terminal 1: Ejecutar servidor
uvicorn src.main:app --reload

# Terminal 2: Probar webhook (local)
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola, ¿hacen apps?"}'
```

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

### 🟦 Fase 3: Conexión de API Externa e Inteligencia Generativa (Completado)
* ✅ Integración del SDK oficial de OpenAI con modelo `gpt-4o-mini`.
* ✅ Validación en Meta for Developers para adquirir `PHONE_NUMBER_ID`.
* ✅ Parseo correcto de estructura JSON de WhatsApp Cloud API.
* ✅ System Prompt v3.0+ basado en State Routing (sin loops).

### 🟦 Fase 3.5: Mejora del Sistema de Clasificación (Actual)
* ✅ **State Routing Inteligente**: Clasificación binaria ESTADO A (Exploración) vs ESTADO B (Captura).
* ✅ **Detección de Intención**: Categorización automática (E-commerce, SPA, Sistema, PWA, API, Gestión).
* ✅ **Scoring de Leads**: Hot (ready) / Warm (interested) / Cold (exploratory).
* ✅ **Preguntas de Calificación**: Budget, timeline, industria (opcional, antes de derivar).
* ✅ **Manejo de Objeciones**: Respuestas inteligentes a preguntas sobre precio, tiempo, equipo.

### 🚀 Fase 4: Persistencia de Datos y Gestión de Contexto (Opcional)
**Depende de decisión estratégica** (Opción A: WhatsApp directo vs Opción B/C: Dashboard + DB)

Si se implementa:
* Integración de PostgreSQL en Railway mediante SQLAlchemy ORM.
* Tabla `conversations`: Guardar historial de chats por cliente.
* Tabla `leads`: Almacenar información de leads calificados con scores.
* Tabla `metrics`: Analytics de conversión (consultas → leads → proyectos).
* Sistema de gestión de contexto conversacional basado en número de teléfono.

### 🎨 Fase 5: Widget Web Flotante (Opcional)
**Depende de Fase 4**

* React component embebible como iframe en `gbsolucionesdigitales.com.ar`.
* Diseño Mobile-First con identidad visual.
* Conexión a backend FastAPI.
* Cierre automático de conversación o persistencia.

### 🎯 Fase 6: Dashboard Admin (Opcional)
**Depende de Fase 4**

* React.js frontend exclusivo para desarrolladores de GB.
* **Funcionalidades**:
  * Listado de leads con scoring (Hot/Warm/Cold).
  * Visualización de historial completo de conversación.
  * Botón "Abrir en WhatsApp" (link pre-rellenado con contexto).
  * Búsqueda y filtros por intención, fecha, score.
  * Etiquetar leads (en seguimiento, cerrado, rechazado).
  * Asignación a desarrollador específico.
* **Métricas**: Tasa de conversión, tiempo promedio de respuesta, ROI.

### 📊 Fase 7: Notificaciones en Tiempo Real (Opcional)
**Depende de Fase 4**

* Webhook automático cuando ESTADO B (lead calificado).
* Múltiples destinos: Email + Discord + Slack (simultáneamente).
* Link pre-rellenado a WhatsApp para respuesta inmediata.

### 📈 Fase 8: Analytics Avanzadas (Opcional)
**Depende de Fase 4**

* Dashboard de métricas en tiempo real.
* Conversión de leads (consultas → derivaciones → proyectos cerrados).
* Problemas más consultados (para SEO y marketing).
* Tiempo promedio de respuesta.
* ROI por canal (WhatsApp directo, web, referencias).

---

## 📊 Monitoreo y Mejora del Bot

### KPIs Principales a Trackear

| Métrica | Target | Cómo Medir |
|---------|--------|-----------|
| **Tasa de loops** | 0% | Revisar logs: ¿ESTADO A→B→A? |
| **Clasificación correcta (A vs B)** | >95% | Sampling manual de 10 conversaciones |
| **Leads derivados (ESTADO B)** | >20% del total | Count ESTADO B / Total mensajes |
| **Respuesta humana** | <2 horas | Trackear si implementas Dashboard |
| **Conversión final** | >10% | Leads calificados → Proyectos cerrados |

### Cómo Mejorar el System Prompt

1. **Recopilar conversaciones**: Guardar chats históricos en logs
2. **Identificar fallos**:
   - ¿El bot cae en loops?
   - ¿Clasifica mal ESTADO A o B?
   - ¿Las preguntas son relevantes?
3. **Ajustar Few-Shot examples**: Agregar casos reales al prompt
4. **Tuning de temperatura**: 
   - `0.3` = Muy robótico, preciso
   - `0.5` = Balance (RECOMENDADO)
   - `0.7` = Muy creativo, riesgoso
5. **Revisar mensajes de derivación**: ¿Suenan naturales o forzados?

---

## 📄 Licencia

Este proyecto es propietario de **GB Soluciones Digitales**. Uso interno únicamente.

---