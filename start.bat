@echo off
title Specx — Specification-Driven Development
echo ============================================
echo   Specx — SDD with Ollama
echo ============================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

:: Create venv if not exists
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
    echo [OK] Ambiente virtual criado.
)

:: Activate venv
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Install dependencies
echo [INFO] Verificando dependencias...
pip install -r requirements.txt --quiet

echo.
echo ============================================
echo   Servidor iniciando em http://localhost:5000
echo   Pressione Ctrl+C para parar
echo ============================================
echo.

:: Start Flask app
python app.py

pause
