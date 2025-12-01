<<<<<<< HEAD
# Viabiliza+África

Sistema completo para desenvolvimento de planos estratégicos, financeiros e de negócio em África.

## 📋 Estrutura do Projeto

```
viabiliza-africa/
├── frontend/              # Interface web
│   └── index.html
├── backend/               # API Python
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py         # Aplicação Flask principal
│   │   ├── models/        # Modelos de dados
│   │   ├── routes/        # Rotas da API
│   │   ├── services/      # Lógica de negócio
│   │   └── utils/         # Utilitários
│   ├── config/            # Configurações
│   ├── tests/             # Testes
│   └── scripts/           # Scripts auxiliares
├── data/                  # Dados persistidos (JSON)
├── docs/                  # Documentação
├── .env.example          # Exemplo de variáveis de ambiente
├── .gitignore
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone <repository-url>
cd viabiliza-africa
```

### 2. Criar ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
```

### 5. Iniciar o servidor

```bash
# Desenvolvimento
python backend/src/app.py

# Ou usando Flask CLI
flask run
```

## 🌐 Acessar a aplicação

- **Frontend:** Abra `frontend/index.html` no navegador
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/api/health

## 📚 Documentação

- [Documentação da API](docs/API.md)
- [Guia de Desenvolvimento](docs/DEVELOPMENT.md)
- [Estrutura de Dados](docs/DATA_STRUCTURE.md)

## 🧪 Testes

```bash
# Executar testes
pytest backend/tests/

# Com cobertura
pytest --cov=backend/src backend/tests/
```

## 🔧 Desenvolvimento

### Estrutura de Código

- **Models:** Definições de dados e estruturas
- **Routes:** Endpoints da API
- **Services:** Lógica de negócio e cálculos
- **Utils:** Funções auxiliares

### Padrões de Código

- PEP 8 para Python
- ESLint/Prettier para JavaScript
- Commits seguindo Conventional Commits

## 📝 Licença

Este projeto é proprietário.

## 👥 Contribuidores

- Equipe Viabiliza+África

=======
# viabiliza-africa
>>>>>>> c3c0931aaf839c673faf5fcdc5fdbc324bc2e2c0
