# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    """Dependency para obtener la base de datos"""
    return db.client[settings.MONGODB_DB_NAME]

async def connect_to_mongo():
    """Conectar a MongoDB"""
    print("🔌 Conectando a MongoDB...")
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Verificar conexión
        await db.client.admin.command('ping')
        print("✅ MongoDB conectado exitosamente")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Cerrar conexión con MongoDB"""
    print("🔌 Cerrando conexión con MongoDB...")
    if db.client:
        db.client.close()
        print("✅ Conexión cerrada")