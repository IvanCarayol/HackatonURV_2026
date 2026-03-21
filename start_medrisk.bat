@echo off
setlocal
title MedRisk Pro Orchestrator
echo ------------------------------------------------------------------
echo      🚀 MedRisk Pro - Lanzador de Sistema Integrado
echo ------------------------------------------------------------------

:: Navegar al directorio raíz del proyecto
cd /d %~dp0

:: Comprobar existencia de venv
if not exist ".venv\Scripts\python.exe" (
    echo ⚠️  Error: No se ha detectado el entorno virtual .venv en la raiz.
    echo Asegurese de haber ejecutado la instalacion previa.
    pause
    exit /b
)

:: Iniciar Backend en una nueva ventana
echo  Arrancando Backend en puerto 8080...
start "MedRisk Backend" cmd /k "color 0B && cd backend\llm-service && ..\..\.venv\Scripts\python.exe app.py"

:: Esperar un momento para el backend
timeout /t 5 /nobreak > nul

:: Iniciar Frontend en una nueva ventana
echo Arrancando Frontend (Vite UI)...
start "MedRisk Frontend" cmd /k "color 0E && cd frontend && npm run dev"

echo.
echo Los sistemas estan siendo lanzados en ventanas independientes.
echo.
echo [!] Info de Acceso:
echo - Frontend: http://localhost:5173 (o puerto indicado por Vite)
echo - Backend:  http://localhost:8080
echo.
echo Presione cualquier tecla para cerrar este lanzador (los servicios seguiran abiertos).
pause > nul
