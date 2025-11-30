# Guia de Troubleshooting - Viabiliza+África

## Erro: "Erro ao conectar com o servidor"

Se você está recebendo este erro ao tentar criar um novo projeto, siga estes passos:

### 1. Verificar se o Backend está rodando

O backend precisa estar rodando para que o frontend possa criar projetos. Para iniciar o backend:

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
python -m backend.src.app
```

Você deve ver uma mensagem como:
```
============================================================
Starting Viabiliza+África Backend API...
============================================================
Environment: development
Frontend: http://localhost:5000
API: http://localhost:5000/api
```

### 2. Verificar se a porta 5000 está disponível

Se a porta 5000 estiver em uso, você pode alterar a porta editando o arquivo `.env`:

```env
FLASK_PORT=5001
```

E então atualizar o frontend para usar a nova porta (ou configurar um proxy).

### 3. Verificar se as dependências estão instaladas

Certifique-se de que todas as dependências estão instaladas:

```bash
pip install -r requirements.txt
```

Dependências principais:
- Flask==3.0.0
- flask-cors==4.0.0
- Flask-SQLAlchemy==3.1.1
- Flask-Migrate==4.0.5

### 4. Verificar se a base de dados foi criada

A base de dados será criada automaticamente na primeira execução em:
- `data/viabiliza_africa.db`

Se houver problemas, você pode inicializar manualmente:

```bash
python backend/scripts/init_db.py
```

### 5. Verificar logs do servidor

Quando o servidor está rodando, você verá logs no terminal. Se houver erros, eles aparecerão lá.

### 6. Testar a API diretamente

Você pode testar se a API está funcionando usando curl ou Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Listar projetos
curl http://localhost:5000/api/projects

# Criar projeto
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste","primeiroAno":2024,"numAnos":5,"unidadeMonetaria":"EUR"}'
```

### 7. Verificar CORS

Se você estiver acessando o frontend de um domínio diferente, pode haver problemas de CORS. O backend está configurado para permitir todas as origens em desenvolvimento.

### 8. Verificar o console do navegador

Abra o DevTools do navegador (F12) e verifique a aba Console para ver erros detalhados.

## Solução Rápida

1. Pare o servidor se estiver rodando (Ctrl+C)
2. Certifique-se de que está no diretório do projeto
3. Ative o ambiente virtual (se estiver usando):
   ```bash
   # Windows
   backend\scripts\setup_venv.bat
   
   # Linux/Mac
   bash backend/scripts/setup_venv.sh
   ```
4. Inicie o servidor novamente:
   ```bash
   # Windows
   backend\scripts\run_dev.bat
   
   # Linux/Mac
   bash backend/scripts/run_dev.sh
   ```
5. Aguarde a mensagem "Starting Viabiliza+África Backend API..."
6. Tente criar o projeto novamente

## Ainda com problemas?

Se o problema persistir:
1. Verifique se há outros processos usando a porta 5000
2. Verifique os logs do servidor para erros específicos
3. Certifique-se de que o Python está na versão 3.8 ou superior
4. Tente limpar o cache do navegador

