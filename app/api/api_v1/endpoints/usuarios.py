# app/api_v1/endpoints/usuarios.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import User, UserCreate, UserStats, UserLogin, Token
from app.db.db import get_database
from datetime import datetime
import bcrypt # <-- ¡NUEVO! Importamos bcrypt directamente
from app.core.config import settings

# --- Configuración de Seguridad ---
# Ya no usamos 'passlib.context.CryptContext'
router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

# --- Funciones de Seguridad (Nuevas, usando bcrypt) ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña plana contra la hasheada."""
    
    # bcrypt requiere que las contraseñas estén en bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    # ¡ARREGLO IMPORTANTE!
    # Truncamos la contraseña en BYTES a 72
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        
    try:
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except Exception as e:
        print(f"Error al verificar contraseña: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hashea una contraseña."""
    
    password_bytes = password.encode('utf-8')

    # ¡ARREGLO IMPORTANTE!
    # Truncamos la contraseña en BYTES a 72
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generamos el 'salt' y hasheamos
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Devolvemos el hash como un string para guardarlo en MongoDB
    return hashed_bytes.decode('utf-8')

# --- Endpoints ---

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db=Depends(get_database)):
    """
    Crear un nuevo usuario.
    Ahora guarda la contraseña de forma segura (hasheada).
    """
    try:
        users_collection = db["users"]
        
        # Verificar si el email ya existe
        if user.email:
            existing = await users_collection.find_one({"email": user.email})
            if existing:
                raise HTTPException(status_code=400, detail="~400: Email ya registrado")
        
        user_dict = user.dict()
        
        # --- ¡CAMBIO IMPORTANTE! ---
        # Hashear la contraseña antes de guardarla
        user_dict["hashed_password"] = get_password_hash(user.password)
        del user_dict["password"] # Borramos la contraseña en texto plano
        
        # Generar un _id único
        user_dict["_id"] = user_dict.get("name", "user") + "_" + str(datetime.utcnow().timestamp())
        user_dict["statistics"] = UserStats().dict()
        user_dict["scores"] = {
            "matematica": 0.0,
            "razonamientoVerbal": 0.0,
            "razonamientoMatematico": 0.0
        }
        user_dict["createdAt"] = datetime.utcnow()
        
        await users_collection.insert_one(user_dict)
        
        # Devolvemos el usuario sin la contraseña hasheada
        del user_dict["hashed_password"] 
        return User(**user_dict)
        
    except HTTPException as e:
        raise e # Re-lanzar excepciones HTTP
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        # Devolvemos el error real al frontend
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: UserLogin, 
    db=Depends(get_database)
):
    """
    Inicia sesión de un usuario y devuelve un token.
    (En este ejemplo simple, devolvemos los datos del usuario)
    """
    users_collection = db["users"]
    user = await users_collection.find_one({"email": form_data.email})
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not user or not verify_password(form_data.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=401, # Error de "No autorizado"
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Si la contraseña es correcta, devolvemos un "token" simple
    return Token(
        access_token="token_falso_jwt_aqui", # Placeholder
        token_type="bearer",
        user_id=str(user["_id"]),
        user_name=user["name"]
    )

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db=Depends(get_database)):
    """Obtener usuario por ID"""
    try:
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return User(**user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str, db=Depends(get_database)):
    """Obtener estadísticas del usuario"""
    try:
        users_collection = db["users"]
        sessions_collection = db["sessions"]
        
        user = await users_collection.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        sessions = await sessions_collection.find(
            {"userId": user_id}
        ).sort("startTime", -1).limit(10).to_list(10)
        
        # Limpiar ObjectId para que sea JSON serializable
        for s in sessions:
            if "_id" in s: s["_id"] = str(s["_id"])
        
        return {
            "success": True,
            "user": user.get("statistics", {}),
            "recentSessions": sessions,
            "scores": user.get("scores", {})
        }
    except Exception as e:
        print(f"Error en stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))