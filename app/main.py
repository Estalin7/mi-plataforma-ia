# app/main.py
from fastapi import FastAPI, Depends # <-- CORREGIDO: 'Depends' AÑADIDO AQUÍ
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.db import connect_to_mongo, close_mongo_connection, get_database
from app.api.api_v1.endpoints import preguntas, usuarios, api
from datetime import datetime

app = FastAPI(
    title="PrepIA API",
    description="Plataforma preuniversitaria con Google Gemini IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    print("=" * 60)
    print("🚀 PrepIA API - Iniciado correctamente")
    print("=" * 60)
    print(f"📚 Documentación: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🤖 IA: {settings.GEMINI_MODEL}")
    print(f"💾 Base de datos: {settings.MONGODB_DB_NAME}")
    print(f"🌐 Puerto: {settings.PORT}")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Incluir routers
app.include_router(api.router)
app.include_router(preguntas.router)
app.include_router(usuarios.router)

# Ruta raíz
@app.get("/")
async def root():
    return {
        "message": "🚀 PrepIA API con Google Gemini",
        "version": "1.0.0",
        "status": "online",
        "ai_model": settings.GEMINI_MODEL,
        "docs": "/docs"
    }

# Health check
@app.get("/health")
async def health_check(db=Depends(get_database)): # <-- AHORA 'Depends' SÍ ESTÁ DEFINIDO
    gemini_status = "✅ Configurado" if settings.GEMINI_API_KEY else "❌ No configurado"
    db_status = "desconectado"
    try:
        await db.command('ping')
        db_status = "conectado"
    except Exception:
        pass
        
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "online",
            "gemini": gemini_status,
            "mongodb": db_status
        }
    }