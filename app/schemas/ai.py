# app/schemas/ai.py
from pydantic import BaseModel
from typing import List, Optional

class ExplanationRequest(BaseModel):
    question: str
    userAnswer: str
    correctAnswer: str
    subject: str
    userId: str

class ExplanationResponse(BaseModel):
    success: bool
    explanation: str

class AdaptiveQuestionRequest(BaseModel):
    userId: str
    subject: str

class QuestionResponse(BaseModel):
    question: str
    options: List[str]
    correct: int
    explanation: str
    difficulty: str
    topic: str

class AdaptiveQuestionResponse(BaseModel):
    success: bool
    question: QuestionResponse

class ChatRequest(BaseModel):
    userId: str
    message: str

class ChatResponse(BaseModel):
    success: bool
    message: str

class AnalysisResponse(BaseModel):
    success: bool
    analysis: str

class StudyPlanRequest(BaseModel):
    userId: str
    targetDate: str
    targetScore: int

class StudyPlanResponse(BaseModel):
    success: bool
<<<<<<< HEAD
    plan: dict
=======
    plan: dict

# En app/schemas/ai.py

class ExamRequest(BaseModel):
    area: str = "C"
    difficulty: str = "intermedio"
    topics: List[str] = ["Matemática", "Lenguaje", "Historia", "Psicología", "Biología"]

class ExamResponse(BaseModel):
    success: bool
    questions: List[dict]

# Agrega esto al final de app/schemas/ai.py

class ExamRequest(BaseModel):
    area: str
    topics: List[str]

class ExamResponse(BaseModel):
    success: bool
    questions: List[dict]
>>>>>>> 9a223186a942271eb8696222b87d6c994a655e83
