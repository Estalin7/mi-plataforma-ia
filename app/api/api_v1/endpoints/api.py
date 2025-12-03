# app/api_v1/endpoints/api.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.ai import (
    ExplanationRequest, ExplanationResponse,
    AdaptiveQuestionRequest, AdaptiveQuestionResponse,
    ChatRequest, ChatResponse,
    AnalysisResponse, StudyPlanRequest, StudyPlanResponse
)
from app.services.gemini_service import gemini_service
from app.db.db import get_database # <-- CORREGIDO
from datetime import datetime

router = APIRouter(prefix="/api/ai", tags=["AI"])

@router.post("/explain", response_model=ExplanationResponse)
async def generate_explanation(request: ExplanationRequest, db=Depends(get_database)):
    """Genera explicación personalizada con Gemini"""
    try:
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": request.userId})
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
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

@router.post("/adaptive-question", response_model=AdaptiveQuestionResponse)
async def get_adaptive_question(request: AdaptiveQuestionRequest, db=Depends(get_database)):
    """Obtiene pregunta adaptativa generada por Gemini"""
    try:
        users_collection = db["users"]
        sessions_collection = db["sessions"]
        
        user = await users_collection.find_one({"_id": request.userId})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Obtener sesiones recientes
        recent_sessions = await sessions_collection.find(
            {"userId": request.userId}
        ).sort("startTime", -1).limit(10).to_list(10)
        
        # Calcular rendimiento
        total_questions = sum(len(s.get("questions", [])) for s in recent_sessions)
        correct_answers = sum(
            sum(1 for q in s.get("questions", []) if q.get("correct", False))
            for s in recent_sessions
        )
        
        # Identificar temas débiles
        topic_performance = {}
        for session in recent_sessions:
            for q in session.get("questions", []):
                topic = q.get("topic")
                if topic:
                    if topic not in topic_performance:
                        topic_performance[topic] = {"correct": 0, "total": 0}
                    topic_performance[topic]["total"] += 1
                    if q.get("correct"):
                        topic_performance[topic]["correct"] += 1
        
        weak_topics = [
            topic for topic, stats in topic_performance.items()
            if stats["total"] >= 3 and stats["correct"] / stats["total"] < 0.6
        ]
        
        question = await gemini_service.generate_adaptive_question(
            subject=request.subject,
            user_level=user.get("level", "principiante"),
            weak_topics=weak_topics if weak_topics else ["general"],
            recent_performance={"correct": correct_answers, "total": total_questions or 1}
        )
        
        return AdaptiveQuestionResponse(success=True, question=question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest, db=Depends(get_database)):
    """Chat conversacional con el tutor IA"""
    try:
        users_collection = db["users"]
        sessions_collection = db["sessions"]
        
        user = await users_collection.find_one({"_id": request.userId})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Calcular contexto
        recent_sessions = await sessions_collection.find(
            {"userId": request.userId}
        ).sort("startTime", -1).limit(10).to_list(10)
        
        total_questions = sum(len(s.get("questions", [])) for s in recent_sessions)
        correct_answers = sum(
            sum(1 for q in s.get("questions", []) if q.get("correct", False))
            for s in recent_sessions
        )
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Identificar materias débiles
        scores = user.get("scores", {})
        weak_subjects = [subject for subject, score in scores.items() if score < 60]
        
        context = {
            "userName": user.get("name", "Estudiante"),
            "userLevel": user.get("level", "principiante"),
            "accuracy": accuracy,
            "weakSubjects": weak_subjects
        }
        
        response = await gemini_service.chat_with_tutor(
            user_id=request.userId,
            message=request.message,
            context=context
        )
        
        return ChatResponse(success=True, message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{user_id}", response_model=AnalysisResponse)
async def analyze_study_pattern(user_id: str, db=Depends(get_database)):
    """Analiza el patrón de estudio del estudiante"""
    try:
        users_collection = db["users"]
        sessions_collection = db["sessions"]
        
        user = await users_collection.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        sessions = await sessions_collection.find({"userId": user_id}).to_list(1000)
        
        if len(sessions) == 0:
            return AnalysisResponse(
                success=True,
                analysis="🎓 Aún no tienes suficientes datos para un análisis completo. ¡Empieza a practicar!"
            )
        
        # Calcular datos de sesión
        total_minutes = 0
        for s in sessions:
            if "endTime" in s and "startTime" in s:
                try:
                    end = datetime.fromisoformat(s["endTime"].replace('Z', '+00:00'))
                    start = datetime.fromisoformat(s["startTime"].replace('Z', '+00:00'))
                    total_minutes += (end - start).seconds // 60
                except:
                    pass
        
        session_data = {
            "sessionsCount": len(sessions),
            "totalMinutes": total_minutes,
            "subjectScores": user.get("scores", {}),
            "preferredTimes": ["mañana", "tarde"],
            "streak": user.get("statistics", {}).get("currentStreak", 0)
        }
        
        analysis = await gemini_service.analyze_study_pattern(user_id, session_data)
        
        return AnalysisResponse(success=True, analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/study-plan", response_model=StudyPlanResponse)
async def generate_study_plan(request: StudyPlanRequest, db=Depends(get_database)):
    """Genera plan de estudio personalizado"""
    try:
        users_collection = db["users"]
        
        user = await users_collection.find_one({"_id": request.userId})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user_profile = {
            "level": user.get("level", "principiante"),
            "currentScore": user.get("statistics", {}).get("averageScore", 0),
            "subjectScores": user.get("scores", {})
        }
        
        plan = await gemini_service.generate_study_plan(
            user_profile=user_profile,
            target_date=request.targetDate,
            target_score=request.targetScore
        )
        
        # Guardar plan en usuario
        await users_collection.update_one(
            {"_id": request.userId},
            {"$set": {"studyPlan": plan}}
        )
        
        return StudyPlanResponse(success=True, plan=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/{user_id}")
async def get_motivational_feedback(user_id: str, db=Depends(get_database)):
    """Genera feedback motivacional"""
    try:
        users_collection = db["users"]
        sessions_collection = db["sessions"]
        
        user = await users_collection.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Sesiones de hoy
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_sessions = await sessions_collection.find({
            "userId": user_id,
            "startTime": {"$gte": today_start.isoformat()}
        }).to_list(100)
        
        total_questions = sum(len(s.get("questions", [])) for s in today_sessions)
        correct_answers = sum(
            sum(1 for q in s.get("questions", []) if q.get("correct", False))
            for s in today_sessions
        )
        
        time_spent = 0
        for s in today_sessions:
            if "endTime" in s and "startTime" in s:
                try:
                    end = datetime.fromisoformat(s["endTime"].replace('Z', '+00:00'))
                    start = datetime.fromisoformat(s["startTime"].replace('Z', '+00:00'))
                    time_spent += (end - start).seconds // 60
                except:
                    pass
        
        performance = {
            "questionsAnswered": total_questions,
            "correctAnswers": correct_answers,
            "timeSpent": time_spent,
            "streak": user.get("statistics", {}).get("currentStreak", 0),
            "trending": "estable"
        }
        
        context = {
            "mood": "motivado",
            "goal": user.get("goals", {}).get("targetUniversity", "ingresar a la universidad")
        }
        
        feedback = await gemini_service.generate_motivational_feedback(performance, context)
        
        return {"success": True, "feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))