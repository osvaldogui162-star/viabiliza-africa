# Estrutura do Projeto

## Visão Geral

```
viabiliza-africa/
├── frontend/              # Interface web
│   └── index.html         # Aplicação frontend principal
├── backend/               # API Python
│   ├── src/               # Código fonte
│   │   ├── __init__.py
│   │   ├── app.py         # Aplicação Flask principal
│   │   ├── models/        # Modelos de dados
│   │   │   ├── __init__.py
│   │   │   └── storage.py # Operações de armazenamento
│   │   ├── routes/        # Rotas da API
│   │   │   ├── __init__.py
│   │   │   ├── spreadsheet_routes.py
│   │   │   └── health_routes.py
│   │   ├── services/      # Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   └── calculations.py
│   │   └── utils/         # Utilitários
│   │       ├── __init__.py
│   │       └── parsers.py
│   ├── config/            # Configurações
│   │   └── settings.py
│   ├── tests/             # Testes
│   └── scripts/           # Scripts auxiliares
│       ├── setup_venv.bat
│       ├── setup_venv.sh
│       ├── run_dev.bat
│       └── run_dev.sh
├── data/                  # Dados persistidos (JSON)
├── docs/                  # Documentação
│   ├── STRUCTURE.md
│   ├── API.md
│   └── DEVELOPMENT.md
├── logs/                  # Arquivos de log
├── venv/                  # Ambiente virtual Python (não versionado)
├── .env                   # Variáveis de ambiente (não versionado)
├── .env.example           # Exemplo de variáveis de ambiente
├── .gitignore
├── requirements.txt       # Dependências Python
├── setup.py               # Setup do pacote Python
└── README.md              # Documentação principal
```

## Descrição dos Diretórios

### frontend/
Contém a interface web do sistema. Atualmente um arquivo HTML único, mas pode ser expandido para uma estrutura mais complexa.

### backend/
Backend Python com arquitetura modular:

- **src/**: Código fonte principal
  - **app.py**: Ponto de entrada da aplicação Flask
  - **models/**: Modelos de dados e operações de armazenamento
  - **routes/**: Definição de rotas e endpoints da API
  - **services/**: Lógica de negócio e cálculos
  - **utils/**: Funções auxiliares (parsers, formatters)

- **config/**: Configurações da aplicação
  - **settings.py**: Configurações baseadas em variáveis de ambiente

- **tests/**: Testes unitários e de integração

- **scripts/**: Scripts auxiliares para setup e execução

### data/
Armazena dados persistidos em formato JSON. Cada planilha tem seu próprio arquivo.

### docs/
Documentação do projeto:
- **STRUCTURE.md**: Este arquivo
- **API.md**: Documentação da API
- **DEVELOPMENT.md**: Guia de desenvolvimento

### logs/
Arquivos de log da aplicação.

## Padrões de Código

### Python
- Seguir PEP 8
- Type hints quando possível
- Docstrings para todas as funções e classes
- Modularização clara (models, routes, services, utils)

### Estrutura de Arquivos
- Um arquivo por classe/funcionalidade principal
- Nomes descritivos e em snake_case
- `__init__.py` em todos os pacotes

## Convenções de Nomenclatura

- **Arquivos Python**: snake_case (ex: `spreadsheet_routes.py`)
- **Classes**: PascalCase (ex: `DataStorage`)
- **Funções/Métodos**: snake_case (ex: `calculate_inflation_index`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `DATA_DIR`)

## Fluxo de Dados

1. **Frontend** → Faz requisições HTTP para **Backend API**
2. **Routes** → Recebe requisições e valida dados
3. **Services** → Executa lógica de negócio e cálculos
4. **Models/Storage** → Persiste/recupera dados
5. **Utils** → Funções auxiliares (parsing, formatação)

## Ambiente Virtual

O projeto usa `venv` para isolar dependências. O ambiente virtual deve ser criado na raiz do projeto e não é versionado.

## Configuração

As configurações são carregadas de:
1. Variáveis de ambiente (`.env`)
2. Configurações padrão em `backend/config/settings.py`

