@echo off
setlocal enabledelayedexpansion

:: --- MedRisk Pro Orchestrator for Windows ---
:: Este script realiza todas las comprobaciones e instala dependencias si es necesario.

title MedRisk Pro - Lanzador Universal

echo ------------------------------------------------------------------
echo      MedRisk Pro - Preparando Ambiente de Ejecucion
echo ------------------------------------------------------------------

:: 1. Comprobar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no detectado. Por favor, instale Python 3.
    pause
    exit /b
)

:: 2. Comprobar Node.js
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js/NPM no detectado. Por favor, instale Node.js.
    pause
    exit /b
)

:: 3. Configurar Entorno Virtual (Backend)
if not exist ".venv" (
    echo [INFO] Creando entorno virtual .venv...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo al crear el entorno virtual.
        pause
        exit /b
    )
)

echo [INFO] Asegurando dependencias del Backend...
call .venv\Scripts\activate
python -m pip install --upgrade pip >nul
pip install -r backend/llm-service/requirements.txt >nul
if !errorlevel! neq 0 (
    echo [ERROR] Fallo al instalar dependencias del Backend.
    pause
    exit /b
)

:: 4. Configurar Frontend
if not exist "frontend\node_modules" (
    echo [INFO] Instalando dependencias del Frontend (npm install)...
    cd frontend
    call npm install
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo al instalar dependencias del Frontend.
        pause
        exit /b
    )
    cd ..
)

echo ------------------------------------------------------------------
echo      SISTEMA LISTO. Lanzando componentes...
echo ------------------------------------------------------------------

:: Lanzar Backend en nueva ventana
start "MedRisk Backend" cmd /k "call .venv\Scripts\activate && cd backend\llm-service && python app.py"

:: Lanzar Frontend en nueva ventana
start "MedRisk Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo [OK] MedRisk Pro se esta ejecutando.
echo      Frontend: http://localhost:5173
echo      Backend:  http://localhost:8080
echo.
pause
