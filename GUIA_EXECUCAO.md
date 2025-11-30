# 🚀 Guia de Execução - Viabiliza+África

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🔧 Passo a Passo para Executar

### 1. Ativar o Ambiente Virtual

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Instalar/Atualizar Dependências (se necessário)

```bash
pip install -r requirements.txt
```

### 3. Inicializar o Banco de Dados

**Primeira vez ou se precisar recriar o banco:**
```bash
python backend/scripts/init_db.py
```

**Se o banco já existe mas não tem a coluna PIN:**
```bash
python backend/scripts/add_pin_column.py
```

### 4. Iniciar o Servidor Backend

```bash
python backend/src/app.py
```

Você verá uma saída similar a:
```
============================================================
Starting Viabiliza+África Backend API...
============================================================
Environment: development
Frontend: http://localhost:5000
API: http://localhost:5000/api
...
```

### 5. Acessar a Aplicação

O servidor Flask irá:
- Iniciar na porta **5000** (padrão)
- Abrir automaticamente o navegador em modo de desenvolvimento
- Servir o frontend em: `http://localhost:5000`
- API disponível em: `http://localhost:5000/api`

## ✅ Verificar se Está Funcionando

### 1. Health Check da API
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

### 2. Testar Listagem de Projetos
Acesse: http://localhost:5000/api/projects

Deve retornar uma lista de projetos (pode estar vazia se não houver projetos criados).

## 🎯 Funcionalidades Principais

### Criar um Novo Projeto
1. Clique em "Novo Projeto" no dashboard
2. Preencha os campos:
   - Nome do Projeto
   - Primeiro Ano de Projeção
   - Nº Anos de Projeção
   - Unidade Monetária
   - **PIN de 4 dígitos** (obrigatório)
3. Clique em "Criar Projeto"

### Acessar um Projeto Existente
1. Na seção "Projetos Recentes" ou "Meus Projetos"
2. Clique no projeto desejado
3. Digite o PIN de 4 dígitos quando solicitado
4. O projeto será aberto após validação do PIN

## 🔍 Solução de Problemas

### Erro: "Porta 5000 já está em uso"
**Solução:**
- Pare outros processos usando a porta 5000
- Ou altere a porta no arquivo de configuração

### Erro: "Campo obrigatório ausente: pin"
**Solução:**
- Certifique-se de preencher o campo PIN ao criar um projeto
- O PIN deve ter exatamente 4 dígitos numéricos

### Erro: "Database not found" ou erros de banco
**Solução:**
```bash
# Recriar o banco de dados
python backend/scripts/init_db.py
```

### Tela em branco no navegador
**Solução:**
1. Verifique o console do navegador (F12) para erros JavaScript
2. Verifique se o servidor backend está rodando
3. Verifique se está acessando `http://localhost:5000`

### Erro ao listar projetos (500)
**Solução:**
1. Execute o script para adicionar a coluna PIN:
   ```bash
   python backend/scripts/add_pin_column.py
   ```
2. Reinicie o servidor backend

## 📝 Comandos Úteis

### Parar o Servidor
Pressione `Ctrl + C` no terminal onde o servidor está rodando

### Ver Logs do Servidor
Os logs aparecem diretamente no terminal onde você executou `python backend/src/app.py`

### Limpar o Banco de Dados (CUIDADO!)
```bash
python backend/scripts/clear_database.py
```

## 🌐 Endpoints da API

### Projetos
- `GET /api/projects` - Listar todos os projetos
- `POST /api/projects` - Criar novo projeto
- `GET /api/projects/<id>` - Obter projeto específico
- `PUT /api/projects/<id>` - Atualizar projeto
- `DELETE /api/projects/<id>` - Deletar projeto
- `GET /api/projects/current` - Obter projeto atual
- `POST /api/projects/current` - Definir projeto atual
- `POST /api/projects/<id>/verify-pin` - Verificar PIN do projeto

### Health Check
- `GET /api/health` - Verificar status da API

## 🔐 Segurança - PIN dos Projetos

- Cada projeto possui um PIN de 4 dígitos único
- O PIN é obrigatório para criar novos projetos
- O PIN é necessário para acessar projetos existentes
- O PIN não é exposto na API (apenas `hasPin: true/false`)

## 📚 Próximos Passos

- Leia a [Documentação Completa](README.md)
- Veja o [Guia Rápido](QUICKSTART.md)
- Consulte a [Estrutura do Projeto](docs/STRUCTURE.md)

