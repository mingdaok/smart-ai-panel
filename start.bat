@echo off
echo ========================================
echo Starting AI Panel Studio...
echo ========================================

echo Starting Backend Service (FastAPI)...
start "AI Panel Backend" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 3000 --reload"

echo Starting Frontend Service (Vite)...
start "AI Panel Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Services are starting in separate windows...
echo [Frontend URL] http://localhost:5174
echo [Backend URL]  http://localhost:3000
echo.
echo To stop the services, simply close the two new command prompt windows.
echo.
pause
