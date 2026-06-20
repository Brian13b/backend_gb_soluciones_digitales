from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.bot_logic import BotLogic

app = FastAPI()
bot = BotLogic()

app.mount("/static", StaticFiles(directory="public"), name="public")

@app.get("/")
async def read_index():
    return FileResponse("public/index.html")

@app.post("/webhook")
async def handle_message(request: Request):
    data = await request.json()
    mensaje_usuario = data.get("text", "")
    respuesta = bot.procesar(mensaje_usuario)
    return {"status": "ok", "response": respuesta}