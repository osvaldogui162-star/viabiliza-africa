@echo off
REM Script para iniciar servidor de desenvolvimento no Windows

REM Mudar para o diretório raiz do projeto
cd /d "%~dp0\..\.."

echo ========================================
echo Viabiliza+Africa - Servidor de Desenvolvimento
echo ========================================
echo.

REM Verificar se ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute primeiro: backend\scripts\setup_venv.bat
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando servidor...
python backend\src\app.py

pause

