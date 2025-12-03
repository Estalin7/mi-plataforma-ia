# app/services/gemini_service.py
import google.generativeai as genai
from app.core.config import settings
from typing import Dict, List
import json
import re

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # --- ¡CONFIGURACIÓN FINAL! ---
            # Leerá 'gemini-flash-latest' desde tu config.py
            self.model_text = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.model_json = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                generation_config={"response_mime_type": "application/json"}
            )
            
            self.conversation_history: Dict[str, List] = {}
            print(f"✅ Servicio de Gemini inicializado con el modelo: {settings.GEMINI_MODEL}")
        except Exception as e:
            print(f"❌ Error al configurar Gemini: {e}")
            raise
    
    async def generate_explanation(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        subject: str,
        user_level: str
    ) -> str:
        """Genera explicación personalizada con Gemini (modelo de texto)"""
        try:
            prompt = f"""Actúa como un tutor experto en {subject} para estudiantes preuniversarios peruanos de nivel {user_level}.

Pregunta: {question}
Respuesta del estudiante: {user_answer}
Respuesta correcta: {correct_answer}

Proporciona una explicación que incluya:
1. Por qué la respuesta correcta es así (explicación clara y concisa)
2. El error conceptual del estudiante (si lo hay)
3. Un consejo específico para mejorar
4. Un ejemplo similar corto

Sé empático, motivador y didáctico. Usa emojis ocasionalmente. Máximo 200 palabras."""

            response = await self.model_text.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"Error generando explicación: {e}")
            raise
    
    async def generate_adaptive_question(
        self,
        subject: str,
        user_level: str,
        weak_topics: List[str],
        recent_performance: Dict
    ) -> Dict:
        """Genera pregunta adaptativa basada en rendimiento (modelo JSON)"""
        try:
            total = recent_performance.get('total', 1)
            correct = recent_performance.get('correct', 0)
            accuracy = (correct / total * 100) if total > 0 else 50
            
            difficulty = 'medio'
            if accuracy > 80:
                difficulty = 'difícil'
            elif accuracy < 50:
                difficulty = 'fácil'
            
            topics_text = f"Enfócate en estos temas débiles: {', '.join(weak_topics)}" if weak_topics else "Tema general"
            
            prompt = f"""Genera UNA pregunta de {subject} para examen de admisión universitaria peruana.

Nivel del estudiante: {user_level}
Rendimiento reciente: {accuracy:.0f}% de aciertos
{topics_text}
Dificultad requerida: {difficulty}

Responde ÚNICAMENTE con este JSON:
{{
  "question": "texto de la pregunta",
  "options": ["opción A", "opción B", "opción C", "opción D"],
  "correct": 0,
  "explanation": "explicación detallada de por qué la respuesta es correcta",
  "difficulty": "{difficulty}",
  "topic": "tema específico"
}}"""

            # Usamos el modelo JSON
            response = await self.model_json.generate_content_async(prompt)
            # No necesitamos limpiar, Gemini lo entrega en JSON
            return json.loads(response.text)
            
        except Exception as e:
            print(f"Error generando pregunta: {e}")
            raise
    
    async def chat_with_tutor(
        self,
        user_id: str,
        message: str,
        context: Dict
    ) -> str:
        """Chat conversacional con el tutor IA (modelo de texto)"""
        try:
            # Obtener o crear historial
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            history = self.conversation_history[user_id]
            
            # Contexto del sistema
            system_context = f"""Eres un tutor virtual experto y motivador en preparación preuniversitaria peruana.

Información del estudiante:
- Nombre: {context.get('userName', 'Estudiante')}
- Nivel: {context.get('userLevel', 'principiante')}
- Materias débiles: {', '.join(context.get('weakSubjects', [])) or 'no identificadas'}
- Precisión general: {context.get('accuracy', 0):.1f}%

Tu rol:
- Motivar y guiar al estudiante con entusiasmo
- Responder dudas académicas de forma clara
- Sugerir estrategias de estudio efectivas
- Ser empático, paciente y cercano
- Usar emojis para hacer la conversación amigable
- Adaptar tu lenguaje al nivel del estudiante

IMPORTANTE: Nunca des respuestas directas a ejercicios sin explicar el proceso de razonamiento."""

            # Crear chat con historial
            if len(history) == 0:
                history.append({ "role": "user", "parts": [system_context] })
                history.append({ "role": "model", "parts": ["Entendido. Estoy listo para ayudar al estudiante con entusiasmo y dedicación. 📚✨"] })
            
            chat = self.model_text.start_chat(history=history)
            response = await chat.send_message_async(message)
            
            # Actualizar historial (mantener últimos 20 mensajes)
            history.append({ "role": "user", "parts": [message] })
            history.append({ "role": "model", "parts": [response.text] })
            
            if len(history) > 22:  # 20 mensajes + 2 del sistema
                history = history[:2] + history[-20:]
            
            self.conversation_history[user_id] = history
            
            return response.text
        except Exception as e:
            print(f"Error en chat: {e}")
            raise
    
    async def analyze_study_pattern(
        self,
        user_id: str,
        session_data: Dict
    ) -> str:
        """Analiza el patrón de estudio del estudiante (modelo de texto)"""
        try:
            subject_scores_text = "\n".join([
                f"- {subject}: {score}%"
                for subject, score in session_data.get('subjectScores', {}).items()
            ])
            
            prompt = f"""Analiza el patrón de estudio de este estudiante preuniversitario peruano:

📊 DATOS DEL ESTUDIANTE:
- Sesiones completadas: {session_data.get('sessionsCount', 0)}
- Tiempo total de estudio: {session_data.get('totalMinutes', 0)} minutos
- Racha actual: {session_data.get('streak', 0)} días consecutivos
- Horarios preferidos: {', '.join(session_data.get('preferredTimes', ['no determinado']))}

📈 RENDIMIENTO POR MATERIA:
{subject_scores_text}

PROPORCIONA (máximo 300 palabras):
1. 🎯 Análisis del patrón de estudio (fortalezas y debilidad)
2. ⭐ 3 fortalezas principales identificadas
3. 🔧 3 áreas de mejora específicas
4. 📋 Plan de acción concreto (3 pasos accionables)
5. 🎓 Predicción de puntaje en examen real (escala vigesimal 0-20)

Sé motivador, específico y realista. Usa emojis. Enfócate en el contexto peruano."""

            response = await self.model_text.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"Error analizando progreso: {e}")
            raise
    
    async def generate_study_plan(
        self,
        user_profile: Dict,
        target_date: str,
        target_score: int
    ) -> Dict:
        """Genera plan de estudio personalizado (modelo JSON)"""
        try:
            from datetime import datetime
            
            try:
                target = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                days_until_exam = (target - datetime.now()).days
            except ValueError:
                # Si la fecha es inválida, poner un default
                target = datetime.now()
                days_until_exam = 30 # Default

            if days_until_exam <= 0:
                days_until_exam = 30  # Default si la fecha ya pasó
            
            subject_scores_text = "\n".join([
                f"- {subject}: {score}%"
                for subject, score in user_profile.get('subjectScores', {}).items()
            ])
            
            prompt = f"""Crea un plan de estudio personalizado para examen de admisión universitaria peruana:

👤 PERFIL DEL ESTUDIANTE:
- Nivel actual: {user_profile.get('level', 'principiante')}
- Puntaje actual: {user_profile.get('currentScore', 0):.1f}%
- Puntaje objetivo: {target_score}%
- Días disponibles: {days_until_exam}

📊 RENDIMIENTO POR MATERIA:
{subject_scores_text}

Genera un plan SEMANAL detallado en formato JSON:
{{
  "summary": "resumen ejecutivo del plan en 2-3 líneas",
  "weeklyGoals": ["objetivo semana 1", "objetivo semana 2", "objetivo semana 3", "objetivo semana 4"],
  "dailySchedule": [
    {{
      "day": "Lunes",
      "subjects": ["Matemática", "Razonamiento Verbal"],
      "topics": ["Álgebra básica", "Analogías"],
      "estimatedTime": 90,
      "goals": ["Resolver 20 problemas de álgebra"]
    }},
    {{
      "day": "Martes",
      "subjects": ["Razonamiento Matemático"],
      "topics": ["Series numéricas"],
      "estimatedTime": 60,
      "goals": ["Dominar 5 tipos de series"]
    }}
  ],
  "milestones": [
    {{
      "week": 1,
      "goal": "Reforzar bases en matemática",
      "expectedScore": 65
    }},
    {{
      "week": 2,
      "goal": "Mejorar razonamiento verbal",
      "expectedScore": 70
    }}
  ],
  "tips": ["Consejo práctico 1", "Consejo práctico 2", "Consejo práctico 3"]
}}"""

            # Usamos el modelo JSON
            response = await self.model_json.generate_content_async(prompt)
            return json.loads(response.text)
            
        except Exception as e:
            print(f"Error generando plan: {e}")
            raise
    
    async def generate_motivational_feedback(
        self,
        performance: Dict,
        context: Dict
    ) -> str:
        """Genera feedback motivacional personalizado (modelo de texto)"""
        try:
            prompt = f"""Genera un mensaje motivacional personalizado para un estudiante preuniversitario peruano:

📊 RENDIMIENTO DE HOY:
- Preguntas respondidas: {performance.get('questionsAnswered', 0)}
- Respuestas correctas: {performance.get('correctAnswers', 0)}
- Tiempo estudiado: {performance.get('timeSpent', 0)} minutos
- Racha: {performance.get('streak', 0)} días consecutivos

📈 CONTEXTO:
- Tendencia: {performance.get('trending', 'estable')}
- Estado de ánimo: {context.get('mood', 'neutral')}
- Objetivo: {context.get('goal', 'ingresar a la universidad')}

Genera un mensaje de máximo 120 palabras que:
1. 🎉 Reconozca el esfuerzo específico de hoy
2. ⭐ Destaque UN logro concreto
3. 💡 Proporcione UN consejo accionable para mañana
4. 🚀 Termine con motivación energética

Usa un tono cercano, amigable y motivador. Incluye emojis. Enfócate en el contexto peruano."""

            response = await self.model_text.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"Error generando feedback: {e}")
            raise
    
    def clear_conversation_history(self, user_id: str):
        """Limpia el historial de conversación"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]

<<<<<<< HEAD
=======

    # En app/services/gemini_service.py

    async def generate_mock_exam(self, area: str, topics: List[str]) -> List[Dict]:
        """Genera un simulacro de examen completo"""
        try:
            # Limitamos a 20 preguntas por petición para asegurar velocidad y que no se corte.
            # Para 100, tendrías que llamar a esto 5 veces en paralelo o en bucle.
            prompt = f"""Genera un examen de admisión tipo UNT (Universidad Nacional de Trujillo) para el Área {area} (Ciencias de la Persona).
            
            Temas requeridos: {', '.join(topics)}
            Cantidad: Genera 20 preguntas variadas y de alto nivel académico.
            
            Formato OBLIGATORIO JSON (Array de objetos):
            [
              {{
                "id": 1,
                "category": "Materia (ej. Historia)",
                "question": "Texto de la pregunta...",
                "options": ["Opción A", "Opción B", "Opción C", "Opción D", "Opción E"],
                "correct": 0,  (índice 0-4 de la respuesta correcta)
                "explanation": "Breve explicación"
              }}
            ]
            """
            
            response = await self.model_json.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error generando examen: {e}")
            # Retornar lista vacía o error manejado
            return []
# (Avanzado) En app/services/gemini_service.py
    async def generate_mock_exam(self, area: str, topics: List[str]) -> List[Dict]:
        all_questions = []
        # Hacemos 5 iteraciones para llegar a 100 (5 x 20)
        for i in range(5): 
            prompt = f"Genera 20 preguntas de examen de admisión... (Parte {i+1}/5)..."
            response = await self.model_json.generate_content_async(prompt)
            batch = json.loads(response.text)
            all_questions.extend(batch)
        return all_questions
    
# Agrega esto dentro de la clase GeminiService en app/services/gemini_service.py

    async def generate_mock_exam(self, area: str, topics: List[str]) -> List[Dict]:
        """Genera 100 preguntas (5 lotes de 20)"""
        all_questions = []
        topics_str = ", ".join(topics)
        
        try:
            # Generamos 5 lotes de 20 preguntas para evitar errores de tamaño
            for i in range(5):
                prompt = f"""Genera un lote de 20 preguntas de examen de admisión UNT (Área {area}).
                Lote número {i+1} de 5.
                Temas: {topics_str}.
                
                Responde SOLO con este JSON (Array de objetos):
                [
                  {{
                    "category": "Curso",
                    "question": "Pregunta...",
                    "options": ["A", "B", "C", "D", "E"],
                    "correct": 0, 
                    "explanation": "Por qué"
                  }}
                ]"""
                
                response = await self.model_json.generate_content_async(prompt)
                batch = json.loads(response.text)
                all_questions.extend(batch)
                
            return all_questions
        except Exception as e:
            print(f"Error generando examen: {e}")
            return []
>>>>>>> 9a223186a942271eb8696222b87d6c994a655e83
# Instancia global
gemini_service = GeminiService()