# test_gemini.py (en la raíz del proyecto)
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carga las variables de entorno
load_dotenv()

async def test_gemini():
    print('=' * 60)
    print('🧪 PROBANDO CONEXIÓN CON GOOGLE GEMINI')
    print('=' * 60)
    print()
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or 'AQUI_VA_TU_API_KEY' in api_key:
        print('❌ Error: GEMINI_API_KEY no está configurada en .env')
        print('   (Asegúrate de haberla pegado en el archivo .env)')
        print()
        return
    
    try:
        genai.configure(api_key=api_key)
        
        # --- ¡CONFIGURACIÓN FINAL! ---
        # Usamos 'gemini-flash-latest', que SÍ está en tu lista de modelos
        model_name = 'gemini-flash-latest'
        model = genai.GenerativeModel(model_name)
        
        print('✅ API Key detectada')
        print(f'⏳ Enviando pregunta de prueba a {model_name}...')
        print()
        
        prompt = "¿Cuál es la capital del Perú? Responde en una sola palabra."
        response = await model.generate_content_async(prompt) # Usamos async
        
        print('─' * 60)
        print(f'📝 Pregunta: {prompt}')
        print(f'🤖 Respuesta de Gemini: {response.text}')
        print('─' * 60)
        print()
        print('✅ ¡CONEXIÓN EXITOSA CON GOOGLE GEMINI!')
        print('🎉 Tu backend FastAPI está listo para funcionar')
        print()
        
    except Exception as e:
        print()
        print(f'❌ ERROR AL CONECTAR CON GEMINI ({model_name}):')
        print(f'   {str(e)}')
        print()
        
        if '429' in str(e):
            print('💡 ¡ERROR DE CUOTA! (429)')
            print('   Has agotado tu límite de solicitudes gratuitas.')
            print('   Solución: Espera un tiempo (1 hora o 1 día) o habilita la facturación en Google Cloud.')
        else:
            print('💡 Error desconocido. Verifica tu conexión a internet.')
        print()

if __name__ == "__main__":
    asyncio.run(test_gemini())