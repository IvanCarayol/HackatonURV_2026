#!/bin/bash

# --- MedRisk Pro Orchestrator for Linux ---

# Navegar al directorio donde se encuentra el script
cd "$(dirname "$0")"

echo "------------------------------------------------------------------"
echo "     🚀 MedRisk Pro - Lanzador de Sistema Integrado (Linux)"
echo "------------------------------------------------------------------"

# 1. Comprobar existencia del entorno virtual
if [ ! -f ".venv/bin/python" ]; then
    echo "⚠️  Error: No se ha detectado el entorno virtual '.venv' en la raíz."
    echo "Por favor, asegúrese de haber creado el venv y cargado las dependencias."
    exit 1
fi

# 2. Comprobar si existe gnome-terminal para emular el comportamiento de Windows (ventanas separadas)
if command -v gnome-terminal >/dev/null 2>&1; then
    echo "🛠️  Abriendo Backend en nueva ventana..."
    gnome-terminal --title="MedRisk Backend" -- bash -c "cd backend/llm-service && ../../.venv/bin/python app.py; exec bash"
    
    sleep 2

    echo "🌐 Abriendo Frontend en nueva ventana..."
    gnome-terminal --title="MedRisk Frontend" -- bash -c "cd frontend && npm run dev; exec bash"

    echo ""
    echo "✅ Los sistemas han sido lanzados en ventanas independientes."
    echo "[!] Info de Acceso:"
    echo "  - Frontend: http://localhost:5173"
    echo "  - Backend:  http://localhost:8080"
else
    # 3. Fallback: Ejecución en paralelo en la misma terminal si no hay entorno gráfico avanzado
    echo "⚠️  No se detectó gnome-terminal. Ejecutando procesos en paralelo..."
    
    # Función para limpiar procesos al salir
    cleanup() {
        echo "🛑 Deteniendo servicios..."
        kill $(jobs -p)
        exit
    }
    trap cleanup SIGINT

    cd backend/llm-service && ../../.venv/bin/python app.py &
    cd frontend && npm run dev &

    echo ""
    echo "✅ Servicios ejecutándose en segundo plano."
    echo "Presione Ctrl+C para detener ambos."
    wait
fi
