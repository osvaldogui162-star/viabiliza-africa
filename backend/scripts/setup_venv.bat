@echo off
REM Script para criar e configurar ambiente virtual no Windows

REM Mudar para o diretório raiz do projeto
cd /d "%~dp0\..\.."

echo ========================================
echo Viabiliza+Africa - Setup Ambiente Virtual
echo ========================================
echo.
echo Diretorio atual: %CD%
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)

echo Criando ambiente virtual...
python -m venv venv

if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual!
    pause
    exit /b 1
)

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Instalando dependencias...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt

if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Ambiente virtual configurado com sucesso!
echo ========================================
echo.
echo Para ativar o ambiente virtual, execute:
echo   venv\Scripts\activate
echo.
echo Para iniciar o servidor, execute:
echo   python backend\src\app.py
echo.
pause

