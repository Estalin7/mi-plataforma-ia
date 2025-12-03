# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # MongoDB
    # Definimos la URL con un valor por defecto (o la tomará de las variables si existe)
    MONGODB_URL: str = "mongodb+srv://prepia_user:oWV1vrnRtbosgPOO@cluster0.gsqytqw.mongodb.net/"
    MONGODB_DB_NAME: str = "prepia_db"
    
    # Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-flash-latest" 
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "mi-clave-secreta-super-dificil-de-adivinar-12345"
    ALGORITHM: str = "HS265"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env" 
        case_sensitive = True
        # --- ¡ESTA ES LA LÍNEA MÁGICA! ---
        extra = "ignore" 

settings = Settings()
