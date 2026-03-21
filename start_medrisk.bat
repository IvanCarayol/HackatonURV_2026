@echo off
setlocal enabledelayedexpansion

:: --- MedRisk Pro Orchestrator for Windows (Robust Version) ---

title MedRisk Pro - Lanzador Universal (Soporte Local + Docker)

echo ------------------------------------------------------------------
echo      🚀 MedRisk Pro - Preparando Ambiente de Ejecucion (Win)
echo ------------------------------------------------------------------

:: 1. Comprobaciones de Instalacion (Python/Node)
where python >nul 2>nul
if %errorlevel% neq 0 ( echo [ERROR] Python no detectado.; pause; exit /b )
where npm >nul 2>nul
if %errorlevel% neq 0 ( echo [ERROR] Node.js/NPM no detectado.; pause; exit /b )

:: 2. Asegurar el Entorno Virtual (Local)
if not exist ".venv" (
    echo [🛠️] Creando entorno virtual .venv...
    python -m venv .venv
)
echo [📦] Asegurando dependencias del Backend...
call .venv\Scripts\activate
pip install -r backend/llm-service/requirements.txt >nul 2>&1

:: 3. Asegurar/Reparar Frontend (Deteccion de Basura entre OS)
if not exist "frontend\node_modules" (
    echo [📦] Instalando dependencias del Frontend por primera vez...
    cd frontend && call npm install && cd ..
) else (
    :: Si el binario vite.cmd no existe, es que vienen de otro OS o estan corruptas
    if not exist "frontend\node_modules\.bin\vite.cmd" (
        echo [⚠️] Dependencias incompatibles o corruptas (Linux/Mac detectado).
        echo [🔥] Forzando re-instalacion del Frontend para Windows...
        cd frontend && rd /s /q node_modules && del package-lock.json >nul 2>&1 && call npm install && cd ..
    )
)

echo ------------------------------------------------------------------
set /p run_docker="¿Desea lanzar el Backend usando Docker Compose? (y/n): "
echo ------------------------------------------------------------------

if "%run_docker%"=="y" (
    where docker-compose >nul 2>nul
    if !errorlevel! equ 0 (
        echo [🐳] Iniciando Backend con Docker Compose...
        cd backend && docker-compose up -d && cd ..
        echo [🌐] Iniciando Frontend local...
        cd frontend && npm run dev
    ) else (
        echo [ERROR] No se ha encontrado Docker Desktop en este sistema.
        pause
    )
) else (
    :: Modo Local Tradicional
    echo [🚀] Lanzando Backend y Frontend localmente...
    start "MedRisk Backend" cmd /k "call .venv\Scripts\activate && cd backend\llm-service && python app.py"
    start "MedRisk Frontend" cmd /k "cd frontend && npm run dev"
    
    echo.
    echo [OK] MedRisk Pro se esta ejecutando.
    echo      Frontend: http://localhost:5173
    echo      Backend:  http://localhost:8080
)
pause
