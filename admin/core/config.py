import os
from typing import List
 
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas
    
    API_TITLE: str = "GB Admin Panel API"
    API_VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://admin.gbsolucionesdigitales.com.ar"
    ]
    
    ENVIRONMENT: str = os.getenv("API_ENV", "development")
 
settings = Settings()