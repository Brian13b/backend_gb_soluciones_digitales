from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bot.database import engine
from shared.models import Base
from bot.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GB Soluciones Digitales - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.gbsolucionesdigitales.com.ar", "https://gbsolucionesdigitales.com.ar"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}