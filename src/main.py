import os
from fastapi.responses import FileResponse
import httpx
from fastapi import FastAPI, Request, HTTPException
from src.bot_logic import BotLogic

app = FastAPI()
bot = BotLogic()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.get("/")
async def read_index():
    return FileResponse("public/index.html")

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Ruta de verificación"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado exitosamente por Meta!")
        return int(challenge)
    raise HTTPException(status_code=403, detail="Error de verificación")

@app.post("/webhook")
async def handle_message(request: Request):
    """Recepción y procesamiento de mensajes entrantes"""
    data = await request.json()
    
    if "text" in data:
        mensaje_usuario = data["text"]
        print(f"Mensaje desde la Web: {mensaje_usuario}")
        respuesta_ia = bot.procesar(mensaje_usuario)
        return {"status": "ok", "response": respuesta_ia}
    
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            mensaje_obj = messages[0]
            
            # Solo procesamos texto, ignoramos otros tipos de mensajes por simplicidad. Futuras mejoras podrían incluir imágenes, stickers, etc.
            if mensaje_obj.get("type") == "text":
                mensaje_usuario = mensaje_obj.get("text", {}).get("body", "")
                numero_cliente = mensaje_obj.get("from")
                
                print(f"Mensaje entrante de {numero_cliente}: {mensaje_usuario}")
                
                respuesta_ia = bot.procesar(mensaje_usuario)
                
                # await enviar_mensaje_whatsapp(numero_cliente, respuesta_ia)
                
    except Exception as e:
        print(f"Error parseando el webhook de Meta: {e}")
        
    # Siempre debemos devolver 200 OK rapido para que Meta no reintente el envio
    return {"status": "ok"}

async def enviar_mensaje_whatsapp(numero, texto):
    """Ejecuta un POST a la Graph API de Meta para enviar la respuesta"""
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
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