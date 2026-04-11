# 🎓 PrepIA Backend - FastAPI + Google Gemini

Backend completo para plataforma de preparación preuniversitaria con **FastAPI** y **Google Gemini AI** .

##  Características

 **API REST Moderna**
- FastAPI con documentación automática
- Async/await para alto rendimiento
- Validación de datos con Pydantic
- Type hints completos

 **Inteligencia Artificial**
- Google Gemini 1.5 Flash (Gratis)
- Preguntas adaptativas en tiempo real
- Explicaciones personalizadas
- Chat conversacional inteligente
- Análisis de progreso con IA
- Planes de estudio personalizados

 **Base de Datos**
- MongoDB con Motor (async)
- Esquemas flexibles
- Almacenamiento escalable



##  Obtener API Key de Gemini (GRATIS)

1. Visita: https://aistudio.google.com/app/apikey
2. Haz clic en "Create API Key"
3. Copia la key generada
4. Pégala en el archivo `.env`:
```env
GEMINI_API_KEY=tu_key_aqui
```

##  Estructura del Proyecto
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
