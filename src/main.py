from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.api.routes import router

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

@app.get("/")
async def read_index():
    return FileResponse("public/index.html")