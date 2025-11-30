#!/bin/bash
# Script para iniciar servidor de desenvolvimento no Linux/Mac

# Mudar para o diretório raiz do projeto
cd "$(dirname "$0")/../.."

echo "========================================"
echo "Viabiliza+África - Servidor de Desenvolvimento"
echo "========================================"
echo ""

# Verificar se ambiente virtual existe
if [ ! -f "venv/bin/activate" ]; then
    echo "ERRO: Ambiente virtual não encontrado!"
    echo "Execute primeiro: bash backend/scripts/setup_venv.sh"
    exit 1
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo ""
echo "Iniciando servidor..."
python backend/src/app.py

