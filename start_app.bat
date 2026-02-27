@echo off
title Groww Data API Server
echo Starting Groww Data API Server...

REM Check if venv exists
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please create one named 'venv' and install requirements.
    pause
    exit /b
)

REM Kill any process using port 8000
echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    if NOT "%%a"=="0" (
        echo Found zombie process %%a on port 8000, terminating...
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the FastAPI server via Uvicorn
echo Starting Uvicorn on port 8000. Press Ctrl+C to stop the server...
start http://127.0.0.1:8000/docs
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload

pause
