# app/api_v1/endpoints/preguntas.py
from fastapi import APIRouter, HTTPException, Depends
from app.db.db import get_database # <-- CORREGIDO
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/sesiones", tags=["Sesiones"])

class QuestionResult(BaseModel):
    questionId: Optional[str] = None
    question: str
    userAnswer: int
    correct: bool
    timeSpent: int
    topic: Optional[str] = None

class SessionCreate(BaseModel):
    userId: str
    subject: str
    questions: List[QuestionResult]
    startTime: datetime
    endTime: datetime
    score: float

@router.post("/")
async def create_session(session: SessionCreate, db=Depends(get_database)):
    """Crear una nueva sesión de estudio"""
    try:
        sessions_collection = db["sessions"]
        users_collection = db["users"]
        
        session_dict = session.dict()
        
        # Convertir datetimes a strings ISO 8601
        session_dict["startTime"] = session_dict["startTime"].isoformat()
        session_dict["endTime"] = session_dict["endTime"].isoformat()
        
        result = await sessions_collection.insert_one(session_dict)
        
        # Actualizar estadísticas del usuario
        user = await users_collection.find_one({"_id": session.userId})
        if user:
            stats = user.get("statistics", {})
            stats["questionsAnswered"] = stats.get("questionsAnswered", 0) + len(session.questions)
            stats["correctAnswers"] = stats.get("correctAnswers", 0) + sum(1 for q in session.questions if q.correct)
            
            # Calcular precisión
            if stats["questionsAnswered"] > 0:
                stats["averageScore"] = (stats["correctAnswers"] / stats["questionsAnswered"]) * 100
            
            await users_collection.update_one(
                {"_id": session.userId},
                {"$set": {"statistics": stats}}
            )
        
        return {
            "success": True,
            "sessionId": str(result.inserted_id),
            "message": "Sesión guardada exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_sessions(user_id: str, limit: int = 10, db=Depends(get_database)):
    """Obtener sesiones de un usuario"""
    try:
        sessions_collection = db["sessions"]
        
        sessions = await sessions_collection.find(
            {"userId": user_id}
        ).sort("startTime", -1).limit(limit).to_list(limit)
        
        # Convertir ObjectId a string
        for session in sessions:
            if "_id" in session:
                session["_id"] = str(session["_id"])
        
        return {
            "success": True,
            "sessions": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))