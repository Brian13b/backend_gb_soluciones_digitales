from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from admin.api.routes import auth, conversations, contact_attempts, stats
from admin.database import engine
from shared.models import Base
from admin.core.config import settings
 
# Crear tablas
Base.metadata.create_all(bind=engine)
 
# FastAPI app
app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)
 
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Incluir rutas
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(conversations.router, prefix="/api", tags=["Conversations"])
app.include_router(contact_attempts.router, prefix="/api", tags=["Contact Attempts"])
app.include_router(stats.router, prefix="/api", tags=["Stats"])
 
@app.get("/health")
def health():
    return {"status": "ok"}
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)