@echo off
REM Indonesia Economic Intelligence — Quick Start Script
REM Run this from the project root directory

echo =====================================================
echo  Indonesia Economic Intelligence Platform
echo  Quick Start Script
echo =====================================================
echo.

REM Check Python
python --version 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Create virtual environment if not exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Create .env from example if not exists
IF NOT EXIST ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env and add your OPENAI_API_KEY for AI features.
    echo            BPS_API_KEY is optional (uses embedded data as fallback).
    echo.
)

REM Start the server
echo.
echo Starting Indonesia Economic Intelligence...
echo Open http://localhost:8000 in your browser
echo Press Ctrl+C to stop
echo.

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
