#!/bin/bash

# --- MedRisk Pro Orchestrator for Linux (Versión Robustecida) ---

cd "$(dirname "$0")"

echo "------------------------------------------------------------------"
echo "     🚀 MedRisk Pro - Lanzador Integrado para Linux"
echo "------------------------------------------------------------------"

# 1. Comprobar Prerrequisitos
if ! command -v python3 &> /dev/null; then echo "❌ Error: Python 3 no detectado."; exit 1; fi
if ! command -v npm &> /dev/null; then echo "❌ Error: Node.js/NPM no detectado."; exit 1; fi

# 2. Configurar Entorno Virtual (Backend Local)
if [ ! -d ".venv" ]; then
    echo "🛠️  Creando entorno virtual .venv..."
    python3 -m venv .venv
fi
echo "📦 Asegurando dependencias del Backend..."
source .venv/bin/activate
pip install -r backend/llm-service/requirements.txt > /dev/null 2>&1

# 3. Configurar/Corregir Frontend (node_modules)
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Instalando dependencias del Frontend por primera vez..."
    cd frontend && npm install && cd ..
else
    # Comprobar si los binarios son válidos para Linux (evitar error de Windows a Linux)
    if [ ! -x "frontend/node_modules/.bin/vite" ]; then
        echo "⚠️  Detectados node_modules incompatibles o sin permisos. Reparando..."
        chmod -R +x frontend/node_modules/.bin/
        # Si sigue fallando el binario (por ser .exe de Windows), forzamos npm install parcial
        if ! ./frontend/node_modules/.bin/vite --version &> /dev/null; then
            echo "🔥 Binarios de Windows detectados. Re-instalando frontend para Linux..."
            cd frontend && rm -rf node_modules package-lock.json && npm install && cd ..
        fi
    fi
fi

# 4. Opción para lanzar en Docker
echo "------------------------------------------------------------------"
echo "¿Desea lanzar el Backend usando Docker Compose? (y/n)"
read -t 5 run_docker
if [[ "$run_docker" == "y" ]]; then
    if command -v docker-compose &> /dev/null; then
        echo "🐳 Iniciando Backend con Docker Compose..."
        (cd backend && docker-compose up -d)
        echo "🌐 Lanzando Frontend localmente..."
        (cd frontend && npm run dev)
    else
        echo "❌ docker-compose no encontrado. Continuando en modo local..."
    fi
else
    # modo local
    cleanup() { echo "🛑 Deteniendo servicios..."; kill $(jobs -p); exit; }
    trap cleanup SIGINT

    echo "🛠️  Lanzando Backend local (Puerto 8080)..."
    (.venv/bin/python backend/llm-service/app.py) &
    
    echo "🌐 Lanzando Frontend local (Puerto 5173)..."
    (cd frontend && npm run dev) &
    
    echo "✅ Sistema iniciado."
    wait
fi
