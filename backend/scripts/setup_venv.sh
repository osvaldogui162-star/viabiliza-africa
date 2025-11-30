#!/bin/bash
# Script para criar e configurar ambiente virtual no Linux/Mac

# Mudar para o diretório raiz do projeto
cd "$(dirname "$0")/../.."

echo "========================================"
echo "Viabiliza+África - Setup Ambiente Virtual"
echo "========================================"
echo ""
echo "Diretório atual: $(pwd)"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado!"
    echo "Por favor, instale Python 3.8 ou superior."
    exit 1
fi

echo "Criando ambiente virtual..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar ambiente virtual!"
    exit 1
fi

echo ""
echo "Ativando ambiente virtual..."
source venv/bin/activate

echo ""
echo "Instalando dependências..."
python3 -m pip install --upgrade pip --quiet
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências!"
    exit 1
fi

echo ""
echo "========================================"
echo "Ambiente virtual configurado com sucesso!"
echo "========================================"
echo ""
echo "Para ativar o ambiente virtual, execute:"
echo "  source venv/bin/activate"
echo ""
echo "Para iniciar o servidor, execute:"
echo "  python backend/src/app.py"
echo ""

