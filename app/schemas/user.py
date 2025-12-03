# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime

# --- NUEVO ---
# Schema para el Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserStats(BaseModel):
    questionsAnswered: int = 0
    correctAnswers: int = 0
    totalTimeStudied: int = 0
    currentStreak: int = 0
    averageScore: float = 0.0

class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    level: str = "principiante"

class UserCreate(UserBase):
    email: EmailStr # <-- Asegurarnos de que el email esté al crear
    password: str   # <-- ¡NUEVO! Pedimos la contraseña

class User(UserBase):
    id: str = Field(alias="_id")
    scores: Dict[str, float] = {
        "matematica": 0.0,
        "razonamientoVerbal": 0.0,
        "razonamientoMatematico": 0.0
    }
    statistics: UserStats = UserStats()
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

# --- NUEVO ---
# Schema para la respuesta del Token
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_name: str