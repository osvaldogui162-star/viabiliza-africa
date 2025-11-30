# Configuração de Variáveis de Ambiente

## Criar arquivo .env

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
# Flask Configuration
FLASK_APP=backend/src/app.py
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,file://

# Data Storage
DATA_DIR=data

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# API Configuration
API_VERSION=v1
API_PREFIX=/api

# Features
ENABLE_CALCULATIONS=True
ENABLE_AUTOSAVE=True
AUTOSAVE_INTERVAL=30
```

## Variáveis Importantes

### SECRET_KEY
**IMPORTANTE:** Altere em produção!
- Gere uma chave segura: `python -c "import secrets; print(secrets.token_hex(32))"`
- Nunca commite a chave real no repositório

### FLASK_PORT
Porta onde o servidor será executado (padrão: 5000)

### DATA_DIR
Diretório onde os dados serão armazenados (padrão: data)

### CORS_ORIGINS
Origens permitidas para CORS (separadas por vírgula)

## Produção

Para produção, defina:
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<chave-secreta-forte>
```

