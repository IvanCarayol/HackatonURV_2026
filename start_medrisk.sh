#!/bin/bash

# --- MedRisk Pro Orchestrator for Linux (Completo) ---
# Este script realiza todas las comprobaciones e instale dependencias si es necesario.

cd "$(dirname "$0")"

echo "------------------------------------------------------------------"
echo "     🚀 MedRisk Pro - Lanzador Integrado para Linux"
echo "------------------------------------------------------------------"

# 1. Comprobar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado. Por favor, instálelo."
    exit 1
fi

# 2. Comprobar Node.js / NPM
if ! command -v npm &> /dev/null; then
    echo "❌ Error: Node.js/NPM no está instalado. Por favor, instálelo."
    exit 1
fi

# 3. Configurar Entorno Virtual (Backend)
if [ ! -d ".venv" ]; then
    echo "🛠️  Creando entorno virtual .venv..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el entorno virtual."
        exit 1
    fi
fi

echo "📦 Instalando dependencias del Backend (requirements.txt)..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r backend/llm-service/requirements.txt > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error al instalar dependencias del Backend."
    exit 1
fi

# 4. Configurar Frontend
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Instalando dependencias del Frontend (npm install)..."
    cd frontend && npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar dependencias del Frontend."
        exit 1
    fi
    cd ..
fi

echo "------------------------------------------------------------------"
echo "      SISTEMA LISTO. Lanzando componentes..."
echo "------------------------------------------------------------------"

# Función para limpiar procesos al salir
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $(jobs -p)
    exit
}
trap cleanup SIGINT

# Lanzar en paralelo
(.venv/bin/python backend/llm-service/app.py) &
backend_pid=$!
echo "🛠️  Backend iniciado (PID $backend_pid)."

(cd frontend && npm run dev) &
frontend_pid=$!
echo "🌐 Frontend iniciado (PID $frontend_pid)."

echo ""
echo "✅ MedRisk Pro se está ejecutando."
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8080"
echo "Presione Ctrl+C para finalizar."

wait
