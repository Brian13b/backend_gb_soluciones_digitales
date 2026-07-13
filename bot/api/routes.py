import httpx
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from bot.database import get_db
from shared.schemas import ChatWebRequest, ChatResponse
from bot import crud
from bot.bot_logic import BotLogic
from bot.core.config import settings
from bot.core.security import verify_webhook_signature
from shared.models import Contact, Message

router = APIRouter()
bot = BotLogic()
logger = logging.getLogger(__name__)

LIMITE_MENSAJES = 20
MINUTOS_VENTANA = 3

@router.post("/chat-web", response_model=ChatResponse)
async def chat_web(request_data: ChatWebRequest, db: Session = Depends(get_db)):
    conversation = crud.get_or_create_conversation(db, request_data.session_id, channel="web")

    now = datetime.now(timezone.utc)
    tiempo_limite = now - timedelta(minutes=MINUTOS_VENTANA)
    
    mensajes_recientes = db.query(Message).filter(
        Message.conversation_id == conversation.id,
        Message.role == "user",
        Message.created_at >= tiempo_limite
    ).count()

    if mensajes_recientes >= LIMITE_MENSAJES:
        print(f"⚠️ SPAM DETECTADO (Web): Sesión {request_data.session_id} bloqueada temporalmente.")
        return ChatResponse(
            respuesta="Estás enviando demasiados mensajes. Por favor, esperá unos minutos antes de volver a escribir.",
            estado_actual=conversation.estado
        )

    crud.add_message(db, conversation.id, role="user", content=request_data.mensaje)
    history = crud.get_conversation_history(db, conversation.id)

    contacto_existente = db.query(Contact).filter(Contact.conversation_id == conversation.id).first()
    datos_confirmados = {}
    if contacto_existente:
        if contacto_existente.name: datos_confirmados['nombre'] = contacto_existente.name
        if contacto_existente.email: datos_confirmados['email'] = contacto_existente.email
        if contacto_existente.phone: datos_confirmados['teléfono'] = contacto_existente.phone

    bot_output = bot.procesar(
        request_data.mensaje, 
        history=history, 
        channel="web",
        datos_confirmados=datos_confirmados
    )
    
    respuesta_ia = bot_output.get("respuesta", "Hubo un error al procesar tu consulta.")
    extracted_contact = bot_output.get("extracted_contact", {})

    if extracted_contact:
        name = extracted_contact.get("name")
        email = extracted_contact.get("email")
        phone = extracted_contact.get("phone")
        confidence = extracted_contact.get("extraction_confidence", 0.0)

        if name or email or phone:
            contact = crud.save_contact(
                db=db,
                conversation_id=conversation.id,
                name=name,
                email=email,
                phone=phone,
                confidence_score=confidence
            )
            if contact and (contact.email or contact.phone):
                crud.update_conversation_state(db, conversation.id, estado="CONTACTADA")
                conversation.estado = "CONTACTADA"

    crud.add_message(db, conversation.id, role="assistant", content=respuesta_ia)

    return ChatResponse(
        respuesta=respuesta_ia,
        estado_actual=conversation.estado
    )

async def procesar_whatsapp_background(numero_cliente: str, mensaje_usuario: str, whatsapp_message_id: str = None):
    db_gen = get_db()
    db = next(db_gen)
    conversation = None
    try:
        if crud.message_exists_by_whatsapp_id(db, whatsapp_message_id):
            print(f"↩️ Mensaje {whatsapp_message_id} ya fue procesado antes (reintento de Meta). Se descarta.")
            return

        conversation = crud.get_or_create_conversation(db, session_id=numero_cliente, channel="whatsapp")

        now = datetime.now(timezone.utc)
        db_updated_at = conversation.updated_at
        if db_updated_at.tzinfo is None:
            db_updated_at = db_updated_at.replace(tzinfo=timezone.utc)
        
        tiempo_inactivo = (now - db_updated_at).total_seconds()

        tiempo_limite_spam = now - timedelta(minutes=MINUTOS_VENTANA)
        mensajes_recientes = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.role == "user",
            Message.created_at >= tiempo_limite_spam
        ).count()

        if mensajes_recientes >= LIMITE_MENSAJES:
            if mensajes_recientes == LIMITE_MENSAJES:
                await enviar_mensaje_whatsapp(numero_cliente, "Estás enviando demasiados mensajes. Por favor, esperá unos minutos.")
            return

        if db.query(Message).filter(Message.conversation_id == conversation.id).count() == 0:
            bienvenida = "¡Hola! Soy GiBi, el asistente virtual de GB Soluciones Digitales. ¿En qué te puedo ayudar hoy?"
            primer_mensaje = crud.add_message(db, conversation.id, role="user", content=mensaje_usuario, whatsapp_message_id=whatsapp_message_id)
            crud.add_message(db, conversation.id, role="assistant", content=bienvenida)
            crud.mark_messages_processed(db, [primer_mensaje.id])
            await enviar_mensaje_whatsapp(numero_cliente, bienvenida)
            return

        mensaje_db = crud.add_message(db, conversation.id, role="user", content=mensaje_usuario, whatsapp_message_id=whatsapp_message_id)

        await asyncio.sleep(5)

        ultimo_mensaje = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.role == "user"
        ).order_by(Message.created_at.desc(), Message.id.desc()).first()

        if mensaje_db.id != ultimo_mensaje.id:
            print("Fragmento detectado en WhatsApp. Delegando al último mensaje...")
            return

        lock_adquirido = crud.try_acquire_processing_lock(db, conversation.id)

        if not lock_adquirido:
            lock_adquirido = await _esperar_lock_liberado(db, conversation.id)

            if lock_adquirido:
                ultimo_mensaje = db.query(Message).filter(
                    Message.conversation_id == conversation.id,
                    Message.role == "user"
                ).order_by(Message.created_at.desc(), Message.id.desc()).first()

                if mensaje_db.id != ultimo_mensaje.id:
                    print("Llegó un fragmento más nuevo mientras se esperaba el lock. Delegando...")
                    crud.release_processing_lock(db, conversation.id)
                    return

        if not lock_adquirido:
            print(f"⚠️ No se pudo adquirir el lock de {numero_cliente} tras esperar. Se descarta esta pasada; el próximo mensaje absorberá el buffer pendiente.")
            return

        try:
            fragmentos = crud.get_pending_user_messages(db, conversation.id)
            if not fragmentos:
                return

            mensaje_unificado = " ".join([msg.content for msg in fragmentos])
            print(f"✅ Unificando mensajes para enviar al LLM: '{mensaje_unificado}'")

            if tiempo_inactivo > 86400:
                history = []
            else:
                history = crud.get_conversation_history(db, conversation.id)
                history = [msg for msg in history if msg.get("role") != "user" or msg.get("content") == mensaje_unificado]

            contacto_existente = db.query(Contact).filter(Contact.conversation_id == conversation.id).first()
            datos_confirmados = {}
            if contacto_existente:
                if contacto_existente.name: datos_confirmados['nombre'] = contacto_existente.name
                if contacto_existente.email: datos_confirmados['email'] = contacto_existente.email
                if contacto_existente.phone: datos_confirmados['teléfono'] = contacto_existente.phone

            bot_output = bot.procesar(
                mensaje_unificado,
                history=history,
                channel="whatsapp",
                datos_confirmados=datos_confirmados,
                webhook_phone=crud.normalize_phone_e164(numero_cliente)
            )

            respuesta_ia = bot_output.get("respuesta", "Hubo un error al procesar tu consulta.")
            extracted_contact = bot_output.get("extracted_contact", {})

            if extracted_contact:
                name = extracted_contact.get("name")
                email = extracted_contact.get("email")
                phone = extracted_contact.get("phone")
                confidence = extracted_contact.get("extraction_confidence", 0.0)

                if name or email or phone:
                    contact = crud.save_contact(
                        db=db,
                        conversation_id=conversation.id,
                        name=name,
                        email=email,
                        phone=phone,
                        confidence_score=confidence
                    )
                    if contact and (contact.email or contact.phone):
                        crud.update_conversation_state(db, conversation.id, estado="CONTACTADA")
                        conversation.estado = "CONTACTADA"

            crud.add_message(db, conversation.id, role="assistant", content=respuesta_ia)
            crud.mark_messages_processed(db, [msg.id for msg in fragmentos])

            try:
                await enviar_mensaje_whatsapp(numero_cliente, respuesta_ia)
            except Exception as envio_error:
                logger.error(
                    f"Fallo al enviar la respuesta por WhatsApp a {numero_cliente} (conversation_id={conversation.id}): {envio_error}",
                    exc_info=True
                )
                try:
                    await enviar_mensaje_whatsapp(numero_cliente, "Disculpá, tuvimos un problema técnico. ¿Podés repetir tu consulta?")
                except Exception:
                    logger.error(
                        f"También falló el mensaje de fallback a {numero_cliente} (conversation_id={conversation.id}).",
                        exc_info=True
                    )
        finally:
            crud.release_processing_lock(db, conversation.id)

    except Exception as e:
        conversation_id = conversation.id if conversation else None
        logger.error(
            f"Error en el procesamiento en segundo plano (numero={numero_cliente}, conversation_id={conversation_id}): {e}",
            exc_info=True
        )
    finally:
        db.close()

async def _esperar_lock_liberado(db: Session, conversation_id, max_espera: int = 60, intervalo: int = 2) -> bool:
    transcurrido = 0
    while transcurrido < max_espera:
        await asyncio.sleep(intervalo)
        transcurrido += intervalo
        if crud.try_acquire_processing_lock(db, conversation_id):
            return True
    return False

@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        print("✅ Webhook verificado exitosamente por Meta!")
        return int(challenge)
    raise HTTPException(status_code=403, detail="❌ Error de verificación del webhook")

@router.post("/webhook")
async def handle_message(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    x_hub_signature_256 = request.headers.get("X-Hub-Signature-256")

    if not verify_webhook_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="❌ Firma de webhook inválida.")

    data = await request.json()
    
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            mensaje_obj = messages[0]
            if mensaje_obj.get("type") == "text":
                mensaje_usuario = mensaje_obj.get("text", {}).get("body", "")
                numero_cliente = mensaje_obj.get("from")
                whatsapp_message_id = mensaje_obj.get("id")

                background_tasks.add_task(procesar_whatsapp_background, numero_cliente, mensaje_usuario, whatsapp_message_id)
                
    except Exception as e:
        print(f"Error parseando el webhook de Meta: {e}")
        
    return {"status": "ok"}

async def enviar_mensaje_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v19.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Fallo al enviar mensaje. Meta respondió: {response.text}")