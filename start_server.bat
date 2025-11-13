@echo off
echo Starting AntiCheat API Server...
echo.

cd /d "%~dp0"

REM Try to run using python -m uvicorn
python -m uvicorn main:app --host 127.0.0.1 --port 8000

if errorlevel 1 (
    echo.
    echo Failed to start with 'python -m uvicorn'
    echo Trying alternative method...
    echo.
    python main.py
)

pause

