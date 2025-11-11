#!/bin/bash
# install.sh

echo "=========================================="
echo "🚀 INSTALANDO PREPIA BACKEND"
echo "=========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "👉 Descárgalo desde: https://python.org"
    exit 1
fi

echo "✅ Python $(python3 --version) detectado"
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✨ ¡INSTALACIÓN COMPLETADA!"
echo "=========================================="
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo ""
echo "1️⃣  Obtener API Key de Gemini (GRATIS):"
echo "    👉 https://aistudio.google.com/app/apikey"
echo "    👉 Edita .env y pega tu key"
echo ""
echo "2️⃣  Probar conexión:"
echo "    👉 python test_gemini.py"
echo ""
echo "3️⃣  Iniciar MongoDB:"
echo "    👉 mongod"
echo ""
echo "4️⃣  Iniciar el servidor:"
echo "    👉 python run.py"
echo ""
echo "=========================================="