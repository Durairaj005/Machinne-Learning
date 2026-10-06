@echo off
title AI Handwritten Digit Recognition System
echo ==========================================================
echo Starting AI Handwritten Digit Recognition System
echo ==========================================================
echo.

echo [1/2] Starting FastAPI Backend API on http://127.0.0.1:8000...
start "Backend - FastAPI" cmd /k "cd /d %~dp0backend && python -m uvicorn app:app --port 8000 --reload"

echo [2/2] Starting React + Vite Frontend on http://localhost:5173...
start "Frontend - Vite" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ==========================================================
echo Both services launched in separate windows!
echo - Frontend:  http://localhost:5173
echo - Backend:   http://127.0.0.1:8000
echo - API Docs:  http://127.0.0.1:8000/docs
echo ==========================================================
echo.
pause
