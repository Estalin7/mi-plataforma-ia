# app/api/api_v1/endpoints/api.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.ai import (
    ExplanationRequest, ExplanationResponse,
    AdaptiveQuestionRequest, AdaptiveQuestionResponse,
    ChatRequest, ChatResponse,
    AnalysisResponse, StudyPlanRequest, StudyPlanResponse
)
from app.services.gemini_service import gemini_service
from app.db.db import get_database
from datetime import datetime

router = APIRouter(prefix="/api/ai", tags=["AI"])

# --- ENDPOINT DEL CHAT (El que necesitas) ---
@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest, db=Depends(get_database)):
    """Chat conversacional con el tutor IA"""
    try:
        users_collection = db["users"]
        sessions_collection = db["sessions"]
        
        user = await users_collection.find_one({"_id": request.userId})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Recopilamos contexto básico para que la IA sepa quién es el alumno
        recent_sessions = await sessions_collection.find(
            {"userId": request.userId}
        ).sort("startTime", -1).limit(10).to_list(10)
        
        total_questions = sum(len(s.get("questions", [])) for s in recent_sessions)
        correct_answers = sum(
            sum(1 for q in s.get("questions", []) if q.get("correct", False))
            for s in recent_sessions
        )
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        scores = user.get("scores", {})
        weak_subjects = [subject for subject, score in scores.items() if score < 60]
        
        context = {
            "userName": user.get("name", "Estudiante"),
            "userLevel": user.get("level", "principiante"),
            "accuracy": accuracy,
            "weakSubjects": weak_subjects
        }
        
        # Llamamos al servicio de Gemini
        response = await gemini_service.chat_with_tutor(
            user_id=request.userId,
            message=request.message,
            context=context
        )
        
        return ChatResponse(success=True, message=response)
    except Exception as e:
        print(f"Error en chat: {e}") # Imprimir error en consola del servidor
        raise HTTPException(status_code=500, detail=str(e))

# --- OTROS ENDPOINTS (Explicación, Análisis, etc.) ---

@router.post("/explain", response_model=ExplanationResponse)
async def generate_explanation(request: ExplanationRequest, db=Depends(get_database)):
    try:
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": request.userId})
        if not user: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        explanation = await gemini_service.generate_explanation(
            question=request.question,
            user_answer=request.userAnswer,
            correct_answer=request.correctAnswer,
            subject=request.subject,
            user_level=user.get("level", "principiante")
        )
        return ExplanationResponse(success=True, explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{user_id}", response_model=AnalysisResponse)
async def analyze_study_pattern(user_id: str, db=Depends(get_database)):
    try:
        users_collection = db["users"]
        sessions_collection = db["sessions"]
        user = await users_collection.find_one({"_id": user_id})
        if not user: raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        sessions = await sessions_collection.find({"userId": user_id}).to_list(1000)
        if len(sessions) == 0:
            return AnalysisResponse(success=True, analysis="Aún no tienes datos suficientes.")
            
        session_data = {
            "sessionsCount": len(sessions),
            "totalMinutes": 0, # Simplificado para evitar errores
            "subjectScores": user.get("scores", {}),
            "preferredTimes": ["mañana"],
            "streak": user.get("statistics", {}).get("currentStreak", 0)
        }
        analysis = await gemini_service.analyze_study_pattern(user_id, session_data)
        return AnalysisResponse(success=True, analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
