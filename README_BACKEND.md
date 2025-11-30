# Viabiliza+África - Backend API

Backend Python para o sistema Viabiliza+África, responsável por cálculos financeiros e gestão de dados das planilhas.

## Instalação

1. Certifique-se de ter Python 3.8+ instalado
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

Para iniciar o servidor backend:

```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

## Endpoints da API

### GET `/api/spreadsheet/<sheet_name>`
Obtém os dados de uma planilha específica.

**Exemplo:**
```bash
GET /api/spreadsheet/pressupostos
```

**Resposta:**
```json
{
  "title": "Plano Financeiro",
  "subtitle": "1. - Pressupostos do Projeto",
  "headers": ["Parâmetro", "Inicial", "Ano 1", "Ano 2", "Ano 3", "Ano 4", "Ano 5"],
  "rows": [...]
}
```

### POST `/api/spreadsheet/update`
Atualiza uma célula específica na planilha e recalcula fórmulas.

**Body:**
```json
{
  "sheet": "pressupostos",
  "row_name": "Taxa de Inflação",
  "column_index": 2,
  "value": "2.5%"
}
```

**Resposta:**
```json
{
  "success": true,
  "calculated_values": {
    "Índice de Inflação-2": "1.0250",
    "Índice de Inflação-3": "1.0506"
  }
}
```

### POST `/api/spreadsheet/<sheet_name>/calculate`
Recalcula todas as fórmulas de uma planilha.

**Body:**
```json
{}
```

**Resposta:**
```json
{
  "success": true,
  "calculated_values": {
    "Índice de Inflação-2": "1.0250",
    "Índice de Inflação-3": "1.0506"
  }
}
```

### POST `/api/spreadsheet/<sheet_name>/save`
Salva uma planilha completa.

**Body:**
```json
{
  "title": "Plano Financeiro",
  "subtitle": "1. - Pressupostos do Projeto",
  "headers": [...],
  "rows": [...]
}
```

### GET `/api/health`
Verifica o status do servidor.

## Fórmulas Implementadas

### Índice de Inflação
**Fórmula:** `Índice de Inflação (n) = (1 + Taxa de Inflação (n)) × Índice de Inflação (n-1)`

Esta fórmula é calculada automaticamente quando a Taxa de Inflação é alterada.

### Reserva de Segurança de Tesouraria (RST)
A RST representa o volume mínimo de disponibilidades necessário para a empresa enfrentar atrasos nos recebimentos e/ou antecipações forçadas dos pagamentos.

**Cálculo padrão:** 1.5 meses de receita média mensal

**Fórmula personalizada:** Pode ser configurada como uma porcentagem dos rendimentos.

## Estrutura de Dados

Os dados são armazenados em arquivos JSON na pasta `data/`:
- `data/pressupostos.json`
- `data/investimento.json`
- etc.

## Desenvolvimento

Para desenvolvimento com hot-reload:

```bash
export FLASK_ENV=development
python app.py
```

## Notas

- Os prazos de recebimento e pagamento são medidos em **dias**
- A RST é calculada com base nos Rendimentos quando disponíveis
- Todas as fórmulas são recalculadas automaticamente quando valores são atualizados

