@echo off
REM 5G PCAN-5G Research Platform Startup Script
REM This script starts both backend and frontend simultaneously on Windows

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo   5G CROSS-LAYER DQN PCAN-5G RESEARCH PLATFORM v2.0
echo   Startup Script
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python or add it to your PATH environment variable
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed or not in PATH
    echo Please install Node.js which includes npm
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
cd backend
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some Python dependencies could not be installed
)
cd ..
echo        Complete!
echo.

echo [2/4] Installing Node.js dependencies...
cd frontend
call npm install --silent
if errorlevel 1 (
    echo WARNING: Some Node.js dependencies could not be installed
)
cd ..
echo        Complete!
echo.

echo [3/4] Starting FastAPI Backend on port 8000...
start "5G Backend Server" cmd /k "cd backend && python main.py"
timeout /t 4 /nobreak

echo [4/4] Starting Vite Frontend on port 5173...
start "5G Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================================================
echo   All services started successfully!
echo ================================================================================
echo.
echo   Backend API:             http://localhost:8000
echo   API Documentation:       http://localhost:8000/docs
echo   Interactive API Tester:  http://localhost:8000/redoc
echo   Frontend Dashboard:      http://localhost:5173
echo.
echo ================================================================================
echo.
echo   Note: Two new windows will open for Backend and Frontend
echo   Close those windows to stop the services
echo.

timeout /t 2 /nobreak
start http://localhost:5173

endlocal
