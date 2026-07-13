import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from bot.database import get_db
from shared.schemas import ChatWebRequest, ChatResponse
from shared.models import Contact
from bot import crud
from bot.bot_logic import BotLogic
from bot.core.config import settings
from bot.core.security import verify_webhook_signature

router = APIRouter()
bot = BotLogic()

@router.post("/chat-web", response_model=ChatResponse)
async def chat_web(request_data: ChatWebRequest, db: Session = Depends(get_db)):
    conversation = crud.get_or_create_conversation(db, request_data.session_id, channel="web")

    crud.add_message(db, conversation.id, role="user", content=request_data.mensaje)

    history = crud.get_conversation_history(db, conversation.id)

    contacto_existente = db.query(Contact).filter(Contact.conversation_id == conversation.id).first()
    datos_confirmados = {}
    if contacto_existente:
        if contacto_existente.name: datos_confirmados['nombre'] = contacto_existente.name
        if contacto_existente.email: datos_confirmados['email'] = contacto_existente.email
        if contacto_existente.phone: datos_confirmados['teléfono'] = contacto_existente.phone

    bot_output = bot.procesar(request_data.mensaje, history=history, channel="web", datos_confirmados=datos_confirmados)
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

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Ruta de verificación para Meta"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        print("✅ Webhook verificado exitosamente por Meta!")
        return int(challenge)
    raise HTTPException(status_code=403, detail="❌ Error de verificación del webhook")

@router.post("/webhook")
async def handle_message(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    x_hub_signature_256 = request.headers.get("X-Hub-Signature-256")

    if not verify_webhook_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=401,
            detail="❌ Firma de webhook inválida. Acceso denegado."
        )

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
                
                print(f"Mensaje entrante de {numero_cliente}: {mensaje_usuario}")
                
                conversation = crud.get_or_create_conversation(db, session_id=numero_cliente, channel="whatsapp")
                history = crud.get_conversation_history(db, conversation.id)
                
                if len(history) == 0:
                    bienvenida = "¡Hola! Soy GiBi, el asistente virtual de GB Soluciones Digitales. ¿En qué te puedo ayudar hoy?"
                    crud.add_message(db, conversation.id, role="assistant", content=bienvenida)
                    await enviar_mensaje_whatsapp(numero_cliente, bienvenida)
                    return {"status": "ok"}
                
                crud.add_message(db, conversation.id, role="user", content=mensaje_usuario)

                contacto_existente = db.query(Contact).filter(Contact.conversation_id == conversation.id).first()
                datos_confirmados = {}
                if contacto_existente:
                    if contacto_existente.name: datos_confirmados['nombre'] = contacto_existente.name
                    if contacto_existente.email: datos_confirmados['email'] = contacto_existente.email
                    if contacto_existente.phone: datos_confirmados['teléfono'] = contacto_existente.phone
                
                bot_output = bot.procesar(mensaje_usuario, history=history, channel="whatsapp", datos_confirmados=datos_confirmados, webhook_phone=numero_cliente)
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
                await enviar_mensaje_whatsapp(numero_cliente, respuesta_ia)
                
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