# run.py (en la raíz del proyecto)
import uvicorn
import sys
import os

# Agrega la carpeta 'app' al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.core.config import settings
from app.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO PREPIA API")
    print("=" * 60)
    print()
    print("📍 Configuración:")
    print(f"   • Host: {settings.HOST}")
    print(f"   • Puerto: {settings.PORT}")
    print(f"   • Modo: {'Development (auto-reload)' if settings.DEBUG else 'Production'}")
    print(f"   • Modelo IA: {settings.GEMINI_MODEL}")
    print()
    print("📚 Documentación disponible en:")
    print(f"   • Swagger UI: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"   • ReDoc: http://{settings.HOST}:{settings.PORT}/redoc")
    print()
    print("💡 Presiona CTRL+C para detener el servidor")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app", # Llama a 'app' dentro de 'app/main.py'
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )