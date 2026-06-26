import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas import ChatWebRequest, ChatResponse
from src import crud
from src.bot_logic import BotLogic

router = APIRouter()
bot = BotLogic()

# ==========================================
# RUTAS PARA LA WEB WIDGET
# ==========================================

@router.post("/chat-web", response_model=ChatResponse)
async def chat_web(request_data: ChatWebRequest, db: Session = Depends(get_db)):
    """
    Endpoint para el chat flotante de React.
    Recibe un session_id (anónimo) y el mensaje.
    """
    conversation = crud.get_or_create_conversation(db, request_data.session_id, channel="web")
    
    crud.add_message(db, conversation.id, role="user", content=request_data.mensaje)
    
    history = crud.get_conversation_history(db, conversation.id)
    
    respuesta_ia = bot.procesar(request_data.mensaje, history=history)
    
    crud.add_message(db, conversation.id, role="assistant", content=respuesta_ia)
    
    return ChatResponse(
        respuesta=respuesta_ia,
        estado_actual=conversation.estado
    )

# ==========================================
# RUTAS PARA WHATSAPP (Futuro)
# ==========================================
# WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
# VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
# PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# @router.get("/webhook")
# async def verify_webhook(request: Request):
#     """Ruta de verificación para Meta"""
#     mode = request.query_params.get("hub.mode")
#     token = request.query_params.get("hub.verify_token")
#     challenge = request.query_params.get("hub.challenge")
#     
#     if mode == "subscribe" and token == VERIFY_TOKEN:
#         print("Webhook verificado exitosamente por Meta!")
#         return int(challenge)
#     raise HTTPException(status_code=403, detail="Error de verificación")

# @router.post("/webhook")
# async def handle_message(request: Request, db: Session = Depends(get_db)):
#     """Recepción y procesamiento de mensajes de WhatsApp"""
#     data = await request.json()
#     
#     try:
#         entry = data.get("entry", [])[0]
#         changes = entry.get("changes", [])[0]
#         value = changes.get("value", {})
#         messages = value.get("messages", [])
#         
#         if messages:
#             mensaje_obj = messages[0]
#             if mensaje_obj.get("type") == "text":
#                 mensaje_usuario = mensaje_obj.get("text", {}).get("body", "")
#                 numero_cliente = mensaje_obj.get("from")
#                 
#                 print(f"Mensaje entrante de {numero_cliente}: {mensaje_usuario}")
#                 
#                 # 1. Recuperar o crear conversación usando el teléfono como session_id
#                 conversation = crud.get_or_create_conversation(db, session_id=numero_cliente, channel="whatsapp")
#                 
#                 # 2. Guardar mensaje usuario
#                 crud.add_message(db, conversation.id, role="user", content=mensaje_usuario)
#                 
#                 # 3. Traer historial
#                 history = crud.get_conversation_history(db, conversation.id)
#                 
#                 # 4. Procesar
#                 respuesta_ia = bot.procesar(mensaje_usuario, history=history)
#                 
#                 # 5. Guardar respuesta bot
#                 crud.add_message(db, conversation.id, role="assistant", content=respuesta_ia)
#                 
#                 # 6. Enviar a Meta
#                 await enviar_mensaje_whatsapp(numero_cliente, respuesta_ia)
#                 
#     except Exception as e:
#         print(f"Error parseando el webhook de Meta: {e}")
#         
#     return {"status": "ok"}

# async def enviar_mensaje_whatsapp(numero, texto):
#     """Ejecuta un POST a la Graph API de Meta para enviar la respuesta"""
#     url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": numero,
#         "type": "text",
#         "text": {"body": texto}
#     }
#     
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=payload)
#         if response.status_code != 200:
#             print(f"Fallo al enviar mensaje. Meta respondió: {response.text}")