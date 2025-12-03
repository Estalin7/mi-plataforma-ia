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
    plan: dict