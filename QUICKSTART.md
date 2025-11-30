# Guia Rápido de Início

## 🚀 Início Rápido (5 minutos)

### 1. Configurar Ambiente Virtual

**Windows:**
```bash
backend\scripts\setup_venv.bat
```

**Linux/Mac:**
```bash
bash backend/scripts/setup_venv.sh
```

**Ou manualmente:**
```bash
# Criar venv
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações (opcional)
```

### 3. Iniciar Servidor

**Windows:**
```bash
backend\scripts\run_dev.bat
```

**Linux/Mac:**
```bash
bash backend/scripts/run_dev.sh
```

**Ou manualmente:**
```bash
python backend/src/app.py
```

### 4. Abrir Frontend

Abra `frontend/index.html` no seu navegador.

## ✅ Verificar Instalação

Acesse: http://localhost:5000/api/health

Deve retornar:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "service": "Viabiliza+África API",
  "version": "1.0.0"
}
```

## 📁 Estrutura Criada

Após o setup, você terá:

```
viabiliza-africa/
├── venv/              # Ambiente virtual (criado)
├── data/              # Dados (criado automaticamente)
├── logs/              # Logs (criado automaticamente)
├── frontend/
├── backend/
└── ...
```

## 🔧 Comandos Úteis

### Ativar Ambiente Virtual
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Desativar Ambiente Virtual
```bash
deactivate
```

### Verificar Instalação
```bash
pip list
```

### Atualizar Dependências
```bash
pip install -r requirements.txt --upgrade
```

## ❓ Problemas Comuns

### Python não encontrado
- Instale Python 3.8+ de https://www.python.org/
- Certifique-se de adicionar Python ao PATH durante a instalação

### Erro ao criar venv
- Verifique se tem permissões de escrita no diretório
- Tente executar como administrador (Windows)

### Porta 5000 já em uso
- Altere `FLASK_PORT` no arquivo `.env`
- Ou pare o processo que está usando a porta

## 📚 Próximos Passos

- Leia [README.md](README.md) para documentação completa
- Veja [docs/STRUCTURE.md](docs/STRUCTURE.md) para entender a estrutura
- Consulte [docs/API.md](docs/API.md) para documentação da API

