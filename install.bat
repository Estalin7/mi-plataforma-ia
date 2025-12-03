@echo off
echo ==========================================
echo INSTALANDO PREPIA BACKEND
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Descargalo desde: https://python.org
    pause
    exit /b 1
)

echo Python detectado correctamente
echo.

REM Crear entorno virtual
echo Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo ==========================================
echo INSTALACION COMPLETADA!
echo ==========================================
echo.
echo PROXIMOS PASOS:
echo.
echo 1. Obtener API Key de Gemini (GRATIS):
echo    https://aistudio.google.com/app/apikey
echo    Edita .env y pega tu key
echo.
echo 2. Probar conexion:
echo    python test_gemini.py
echo.
echo 3. Iniciar MongoDB
echo.
echo 4. Iniciar el servidor:
echo    python run.py
echo.
echo ==========================================
pause