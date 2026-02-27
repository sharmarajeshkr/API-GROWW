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

echo Starting Uvicorn on port 8000. Press Ctrl+C to stop the server...

REM Launch a background job to poll the server and open the browser once it's up
start /b cmd /c "for /l %%x in (1, 1, 30) do (curl -s -f -o nul http://127.0.0.1:8000/docs >nul 2>&1 ^&^& (start http://127.0.0.1:8000/docs ^& exit) || timeout /t 1 >nul 2>&1)"

REM Run Uvicorn in the foreground
python -m uvicorn main_api:app --host 127.0.0.1 --port 8000 --reload

pause
