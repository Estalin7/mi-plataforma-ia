# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "prepia_db"
    
    # Gemini
    GEMINI_API_KEY: str
    
    # --- ¡MODELO CORREGIDO! ---
    # Este es el modelo que SÍ está en tu lista de la API
    GEMINI_MODEL: str = "gemini-flash-latest" 
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "mi-clave-secreta-super-dificil-de-adivinar-12345"
    ALGORITHM: str = "HS265"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    # --- ¡CAMBIO IMPORTANTE AQUÍ! ---
    # Permitimos todos los orígenes ("*") para el desarrollo
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        # Le decimos que lea el archivo .env
        env_file = ".env" 
        case_sensitive = True

settings = Settings()