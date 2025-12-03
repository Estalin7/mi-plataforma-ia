# 🎓 PrepIA Backend - FastAPI + Google Gemini

Backend completo para plataforma de preparación preuniversitaria con **FastAPI** y **Google Gemini AI** (100% GRATIS).

## 🌟 Características

✨ **API REST Moderna**
- FastAPI con documentación automática
- Async/await para alto rendimiento
- Validación de datos con Pydantic
- Type hints completos

🤖 **Inteligencia Artificial**
- Google Gemini 1.5 Flash (Gratis)
- Preguntas adaptativas en tiempo real
- Explicaciones personalizadas
- Chat conversacional inteligente
- Análisis de progreso con IA
- Planes de estudio personalizados

💾 **Base de Datos**
- MongoDB con Motor (async)
- Esquemas flexibles
- Almacenamiento escalable

## 🚀 Instalación Rápida

### Windows
```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd PLATAFORMA_IA

# 2. Ejecutar instalador
install.bat

# 3. Configurar API Key
# Edita .env y agrega tu GEMINI_API_KEY

# 4. Probar conexión
python test_gemini.py

# 5. Iniciar servidor
python run.py
```

### Linux/Mac
```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd PLATAFORMA_IA

# 2. Dar permisos y ejecutar
chmod +x install.sh
./install.sh

# 3. Configurar API Key
# Edita .env y agrega tu GEMINI_API_KEY

# 4. Probar conexión
python test_gemini.py

# 5. Iniciar servidor
python run.py
```

## 🔑 Obtener API Key de Gemini (GRATIS)

1. Visita: https://aistudio.google.com/app/apikey
2. Haz clic en "Create API Key"
3. Copia la key generada
4. Pégala en el archivo `.env`:
```env
GEMINI_API_KEY=tu_key_aqui
```

## 📁 Estructura del Proyecto
```
PLATAFORMA_IA/
├── app/
│   ├── api_v1/
│   │   └── endpoints/
│   │       ├── api.py          # Endpoints de IA
│   │       ├── usuarios.py     # Gestión de usuarios
│   │       └── preguntas.py    # Sesiones de estudio
│   ├── core/
│   │   └── config.py           # Configuración
│   ├── schemas/
│   │   ├── user.py             # Schemas de usuario
│   │   └── ai.py               # Schemas de IA
│   ├── services/
│   │   └── gemini_service.py   # Servicio Gemini
│   └── db.py                   # Conexión MongoDB
├── main.py                     # Aplicación principal
├── run.py                      # Script de inicio
├── test_gemini.py              # Test de conexión
├── requirements.txt            # Dependencias
├── .env                        # Variables de entorno
└── README.md
```

## 🔌 Endpoints de la API

### IA (Gemini)
```
POST   /api/ai/explain              # Explicación personalizada
POST   /api/ai/adaptive-question    # Pregunta adaptativa
POST   /api/ai/chat                 # Chat con tutor
GET    /api/ai/analyze/{user_id}   # Análisis de progreso
POST   /api/ai/study-plan           # Plan de estudio
GET    /api/ai/feedback/{user_id}  # Feedback motivacional
```

### Usuarios
```
POST   /api/usuarios/              # Crear usuario
GET    /api/usuarios/{user_id}    # Obtener usuario
PUT    /api/usuarios/{user_id}    # Actualizar usuario
GET    /api/usuarios/{user_id}/stats  # Estadísticas
```

### Sesiones

POST   /api/sesiones/             # Guardar sesión
GET    /api/sesiones/user/{user_id}  # Obtener sesiones

## 📚 Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

bashpython test_gemini.py