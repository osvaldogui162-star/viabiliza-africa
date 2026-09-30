


# ViabilizA+ África

**Plataforma de Business Intelligence com Rastreabilidade Total**

> Especificação técnica completa para desenvolvimento do sistema — v2.0 | Junho 2026

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Problema e Solução](#problema-e-solução)
3. [Objetivos do Sistema](#objetivos-do-sistema)
4. [Arquitetura Funcional](#arquitetura-funcional)
5. [Perfis de Utilizador](#perfis-de-utilizador)
6. [Casos de Uso](#casos-de-uso)
7. [Histórias do Utilizador](#histórias-do-utilizador)
8. [Matriz de Permissões](#matriz-de-permissões)
9. [Regras de Negócio](#regras-de-negócio)
10. [Integrações Externas](#integrações-externas)
11. [Escopo de Implementação](#escopo-de-implementação)
12. [Referências](#referências)

---

## Visão Geral

O **ViabilizA+ África** é uma plataforma SaaS de Business Intelligence financeira voltada para a **elaboração, análise e submissão de estudos de viabilidade de investimento** no contexto africano, com foco particular em **Angola**.

O sistema digitaliza o ciclo completo de um estudo de investimento — desde a recolha de custos reais do mercado local até à submissão regulamentada a instituições financeiras — com **transparência auditável** e **análise quantitativa de nível institucional**.

### Público-alvo

| Segmento | Descrição |
|----------|-----------|
| Analistas financeiros | Especialistas que preparam projetos para bancos e investidores |
| Empresários | Acompanham estudos partilhados e recebem relatórios |
| Consultores | Colaboram em projetos via Kanban e chat |
| Instituições financeiras | BFA, BDA e investidores internacionais |
| Administradores da plataforma | Gestão operacional, auditoria e configuração |

### Base normativa

- Requisitos Funcionais **RF001 a RF080**
- Checklists institucionais **BFA** e **BDA**
- **Aviso BNA 10/2020** (Banco Nacional de Angola)

---

## Problema e Solução

| Problema atual | Solução ViabilizA+ |
|----------------|-------------------|
| Estudos feitos em Excel, sem padronização | Plataforma unificada com 60+ indicadores automáticos |
| Dados de custos desatualizados ou sem fonte | Scraping de mercado (Jumia, Jiji, etc.) + importação Excel |
| Falta de confiança de auditores/investidores | Orçamentos rastreáveis com hash SHA-256 e QR Code |
| Retrabalho para cada instituição | Relatórios nos formatos Internacional, BFA e BDA |
| Submissão lenta aos bancos | Integração via API com BFA/BDA |
| Trabalho em equipa desorganizado | Kanban, chat e partilha de projetos |

---

## Objetivos do Sistema

1. **Automatizar** o cálculo de indicadores de viabilidade financeira (VPL, TIR, ROI, ROE, EBITDA, entre 60+ KPIs).
2. **Garantir rastreabilidade** de todos os dados OPEX/CAPEX com hashes criptográficos e audit trail.
3. **Obter dados reais de mercado** africano via scraping automático de fornecedores locais.
4. **Gerar relatórios regulamentados** prontos para submissão (Internacional, BFA, BDA).
5. **Integrar com bancos** via API para acelerar processos de análise de crédito.
6. **Facilitar colaboração** entre equipas com Kanban, chat e partilha de projetos.
7. **Comercializar** a plataforma via planos e assinaturas com limites por funcionalidade.

---

## Arquitetura Funcional

O sistema é organizado em **7 módulos funcionais** com **39 casos de uso**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ViabilizA+ África                            │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│  Módulo 1   │  Módulo 2   │  Módulo 3   │  Módulo 4             │
│  Auth &     │  Gestão de  │  Ingestão   │  Análise &            │
│  Acesso     │  Projetos   │  Rastreável │  Indicadores          │
├─────────────┼─────────────┼─────────────┼───────────────────────┤
│  Módulo 5   │  Módulo 6   │  Módulo 7   │                       │
│  Tarefas &  │  Relatórios │  Admin &    │                       │
│  Colaboração│             │  Config     │                       │
└─────────────┴─────────────┴─────────────┴───────────────────────┘
```

### Fluxo principal

```
Criar Projeto → Ingerir Dados (Excel/Scraping/Manual)
     → Gerar Orçamento Rastreável → Calcular Indicadores
          → Simulações (Monte Carlo / Sensibilidade)
               → Gerar Relatório (Internacional/BFA/BDA)
                    → Enviar (Email / WhatsApp / API Bancária)
```

---

## Perfis de Utilizador

### 1. Administrador (`admin`)

**Quem é:** Gestor da plataforma, responsável por configuração, auditoria global e gestão de utilizadores.

**Permissões gerais:**
- Acesso total a todos os projetos
- Configuração de APIs de mercado e integração bancária
- Gestão de planos e assinaturas
- Visualização de todos os logs de auditoria
- Anulação de validações

---

### 2. Analista Financeiro (`financial`)

**Quem é:** Especialista que prepara projetos de investimento para submissão a bancos ou investidores.

**Permissões gerais:**
- Criar, editar e excluir os seus próprios projetos
- Importar dados (manual e Excel)
- Executar scraping automático
- Rodar simulações e calcular indicadores
- Gerar relatórios e orçamentos rastreáveis
- Enviar relatórios para bancos via API
- Partilhar projetos com outros utilizadores

---

### 3. Usuário Comum (`user`)

**Quem é:** Colaborador, consultor júnior ou empresário com acesso limitado.

**Permissões gerais:**
- Visualizar projetos partilhados
- Baixar relatórios em PDF
- Participar em chat e tarefas (Kanban)
- Visualizar benchmarks de mercado

**Restrições:**
- Não pode editar projetos
- Não pode importar dados
- Não pode executar simulações
- Não pode enviar relatórios para bancos

---

## Casos de Uso

Total: **39 casos de uso** organizados por módulo.

### Módulo 1 — Autenticação e Gestão de Acesso

| ID | Nome | Ator Principal | Descrição |
|----|------|----------------|-----------|
| UC01 | Registar novo utilizador | Administrador | Cria contas para analistas financeiros e utilizadores comuns |
| UC02 | Fazer login | Todos os utilizadores | Acesso ao sistema com email e palavra-passe |
| UC03 | Recuperar palavra-passe | Todos os utilizadores | Solicita redefinição de palavra-passe por email |
| UC04 | Gerir perfis de acesso | Administrador | Atribui ou revoga permissões (admin/financial/user) |
| UC05 | Ver log de acessos | Administrador | Consulta histórico de logins e ações sensíveis |

---

### Módulo 2 — Gestão de Projetos

| ID | Nome | Ator Principal | Descrição |
|----|------|----------------|-----------|
| UC06 | Criar novo projeto | Analista Financeiro | Preenche dados básicos: nome, setor, país, moeda, investimento |
| UC07 | Listar projetos | Todos os utilizadores | Visualizar projetos com filtros (status, país, setor) |
| UC08 | Editar projeto | Analista Financeiro | Alterar dados (apenas status "Rascunho") |
| UC09 | Excluir projeto | Analista Financeiro | Soft delete (apenas se não houver orçamento aprovado) |
| UC10 | Visualizar detalhes do projeto | Todos os utilizadores | Aceder à página com abas (ingestão, análise, relatórios) |
| UC11 | Partilhar projeto | Analista Financeiro | Convidar outro analista/consultor para colaborar |

---

### Módulo 3 — Ingestão de Dados (Rastreável)

| ID | Nome | Ator Principal | Descrição |
|----|------|----------------|-----------|
| UC12 | Importar dados manualmente | Analista Financeiro | Inserir itens OPEX/CAPEX um a um, com hash de rastreabilidade |
| UC13 | Importar dados via Excel | Analista Financeiro | Upload de Excel com até 1000 linhas; cada linha gera hash |
| UC14 | Executar scraping automático | Analista Financeiro | Busca preços de fornecedores locais (Jumia, Jiji, etc.) |
| UC15 | Selecionar fornecedor | Analista Financeiro | Escolhe o fornecedor mais adequado para cada item |
| UC16 | Gerar orçamento rastreável | Analista Financeiro | Orçamento com QR Code e hashes de auditoria |
| UC17 | Gerar fatura proforma | Analista Financeiro | Fatura para clientes ou bancos a partir do orçamento |
| UC18 | Visualizar audit trail | Analista/Admin | Log completo de alterações com hashes |

---

### Módulo 4 — Análise e Indicadores

| ID | Nome | Ator Principal | Descrição |
|----|------|----------------|-----------|
| UC19 | Calcular indicadores de viabilidade | Analista Financeiro | 60+ indicadores (VPL, TIR, ROI, ROE, EBITDA, etc.) |
| UC20 | Executar Simulação Monte Carlo | Analista Financeiro | 1.000 a 50.000 iterações; distribuição do VPL |
| UC21 | Executar Análise de Sensibilidade | Analista Financeiro | 3 a 10 variáveis; impacto no VPL/TIR |
| UC22 | Comparar benchmarks de mercado | Analista Financeiro | Comparação com médias do setor africano |
| UC23 | Exportar indicadores para Excel | Analista Financeiro | Download da tabela completa de indicadores |

---

### Módulo 5 — Tarefas e Colaboração

| ID | Nome | Ator Principal | Descrição |
|----|------|----------------|-----------|
| UC24 | Criar tarefa no Kanban | Qualquer utilizador | Tarefa com título, descrição, responsável, prazo |
| UC25 | Mover tarefa (arrastar/soltar) | Qualquer utilizador | Atualizar status (A Fazer → Em Andamento → Concluído) |
| UC26 | Criar dependência entre tarefas | Analista Financeiro | Definir precedência entre tarefas |
| UC27 | Enviar mensagem no chat | Qualquer utilizador | Comunicação em tempo real na equipa |

---

### Módulo 6 — Relatórios

| ID | Nome | Ator Principal | Descrição |
|----|------|----------------|-----------|
| UC28 | Gerar relatório Internacional | Analista Financeiro | PDF completo (10 secções) em USD/EUR, PT/EN, com QR Code |
| UC29 | Gerar relatório BFA | Analista Financeiro | PDF conforme Aviso BNA 10/2020, validação de documentos |
| UC30 | Gerar relatório BDA | Analista Financeiro | Formulário BDA (61 páginas), tabela de reembolsos automática |
| UC31 | Enviar relatório por email | Analista Financeiro | Enviar PDF anexo para banco/investidor |
| UC32 | Compartilhar por WhatsApp | Empresário/Analista | Link temporário (7 dias) via WhatsApp |
| UC33 | Imprimir relatório | Qualquer utilizador | Impressão com layout otimizado |
| UC34 | Enviar para banco via API | Analista/Admin | Integração direta com APIs do BFA/BDA |

---

### Módulo 7 — Administração e Configuração

| ID | Nome | Ator Principal | Descrição |
|----|------|----------------|-----------|
| UC35 | Configurar APIs de mercado | Administrador | Adicionar/remover fontes de scraping |
| UC36 | Configurar integração bancária | Administrador | Inserir credenciais das APIs dos bancos |
| UC37 | Gerir templates de orçamento | Administrador | Personalizar modelos de orçamento e fatura |
| UC38 | Consultar logs de auditoria | Administrador | Histórico completo de todas as ações |
| UC39 | Gerir planos e assinaturas | Administrador | Configurar preços e limites por plano |

---

## Histórias do Utilizador

Total: **18 histórias** organizadas por perfil.

### Administrador (`admin`)

| ID | História |
|----|----------|
| **H01** | Como **Administrador**, eu quero **criar e gerir contas de analistas e utilizadores comuns** para que **cada pessoa tenha apenas as permissões necessárias para o seu trabalho**. |
| **H02** | Como **Administrador**, eu quero **configurar as APIs de scraping e integração bancária** para que **os dados de mercado e o envio para bancos funcionem automaticamente**. |
| **H03** | Como **Administrador**, eu quero **consultar os logs de auditoria completos** para que **eu possa rastrear qualquer ação suspeita ou comprovar a origem dos dados**. |
| **H04** | Como **Administrador**, eu quero **definir quais funcionalidades cada plano de assinatura acede** para que **a comercialização seja justa e escalável**. |

---

### Analista Financeiro (`financial`)

| ID | História |
|----|----------|
| **H05** | Como **Analista Financeiro**, eu quero **criar um projeto com os dados básicos da empresa e do investimento** para que **eu comece a estruturar o estudo de viabilidade**. |
| **H06** | Como **Analista Financeiro**, eu quero **importar itens OPEX/CAPEX via Excel** para que **eu não perca tempo digitando item por item**. |
| **H07** | Como **Analista Financeiro**, eu quero **executar scraping automático de preços de fornecedores** para que **os valores sejam reais e atualizados do mercado africano**. |
| **H08** | Como **Analista Financeiro**, eu quero **que cada dado importado tenha um hash SHA-256 registado** para que **investidores e auditores confiem na origem dos números**. |
| **H09** | Como **Analista Financeiro**, eu quero **calcular automaticamente os 60+ indicadores de viabilidade** para que **eu não precise fazer contas manuais nem usar Excel**. |
| **H10** | Como **Analista Financeiro**, eu quero **executar a Simulação Monte Carlo com 10.000 iterações** para que **eu possa mostrar aos investidores a probabilidade de sucesso do projeto**. |
| **H11** | Como **Analista Financeiro**, eu quero **gerar um orçamento rastreável com QR Code** para que **o banco possa verificar a autenticidade dos dados em tempo real**. |
| **H12** | Como **Analista Financeiro**, eu quero **gerar relatórios nos formatos Internacional, BFA e BDA** para que **eu possa submeter o projeto a qualquer instituição sem retrabalho**. |
| **H13** | Como **Analista Financeiro**, eu quero **enviar o relatório diretamente para o banco via API** para que **o processo de análise de crédito seja mais rápido**. |
| **H14** | Como **Analista Financeiro**, eu quero **colaborar com outros analistas no mesmo projeto via chat e tarefas** para que **o trabalho em equipa seja organizado e rastreável**. |

---

### Usuário Comum (`user`)

| ID | História |
|----|----------|
| **H15** | Como **Usuário Comum**, eu quero **visualizar projetos que foram partilhados comigo** para que **eu possa acompanhar o progresso sem ter permissões de edição**. |
| **H16** | Como **Usuário Comum**, eu quero **baixar relatórios em PDF** para que **eu possa apresentar a investidores ou sócios**. |
| **H17** | Como **Usuário Comum**, eu quero **criar e mover tarefas no Kanban** para que **eu organize as minhas atividades no projeto**. |
| **H18** | Como **Usuário Comum**, eu quero **participar do chat do projeto** para que **eu tire dúvidas rapidamente com o analista responsável**. |

---

## Matriz de Permissões

### Autenticação e Acesso

| Ação | Administrador | Analista Financeiro | Usuário Comum |
|------|:-------------:|:-------------------:|:-------------:|
| Fazer login | ✅ | ✅ | ✅ |
| Recuperar palavra-passe | ✅ | ✅ | ✅ |
| Gerir utilizadores (criar/editar/remover) | ✅ | ❌ | ❌ |
| Ver logs de acesso | ✅ | ❌ | ❌ |

### Gestão de Projetos

| Ação | Administrador | Analista Financeiro | Usuário Comum |
|------|:-------------:|:-------------------:|:-------------:|
| Criar projeto | ✅ | ✅ | ❌ |
| Listar projetos | ✅ (todos) | ✅ (os seus) | ✅ (partilhados) |
| Editar projeto (dados básicos) | ✅ (todos) | ✅ (os seus) | ❌ |
| Excluir projeto | ✅ (todos) | ✅ (os seus, rascunho) | ❌ |
| Partilhar projeto | ✅ | ✅ | ❌ |

### Ingestão de Dados

| Ação | Administrador | Analista Financeiro | Usuário Comum |
|------|:-------------:|:-------------------:|:-------------:|
| Importar dados (manual/Excel) | ✅ | ✅ | ❌ |
| Executar scraping automático | ✅ | ✅ | ❌ |
| Gerar orçamento rastreável | ✅ | ✅ | ❌ |
| Visualizar audit trail | ✅ (todos) | ✅ (os seus) | ❌ |

### Análise e Indicadores

| Ação | Administrador | Analista Financeiro | Usuário Comum |
|------|:-------------:|:-------------------:|:-------------:|
| Calcular indicadores | ✅ | ✅ | ❌ |
| Executar Monte Carlo | ✅ | ✅ | ❌ |
| Ver benchmarks | ✅ | ✅ | ✅ (visualização) |

### Tarefas e Colaboração

| Ação | Administrador | Analista Financeiro | Usuário Comum |
|------|:-------------:|:-------------------:|:-------------:|
| Criar tarefa no Kanban | ✅ | ✅ | ✅ |
| Mover tarefa (arrastar/soltar) | ✅ | ✅ | ✅ |
| Enviar mensagem no chat | ✅ | ✅ | ✅ |

### Relatórios

| Ação | Administrador | Analista Financeiro | Usuário Comum |
|------|:-------------:|:-------------------:|:-------------:|
| Gerar relatório (qualquer modelo) | ✅ | ✅ | ✅ |
| Baixar PDF | ✅ | ✅ | ✅ |
| Enviar por email/WhatsApp | ✅ | ✅ | ❌ |
| Enviar para banco via API | ✅ | ✅ | ❌ |

### Administração

| Ação | Administrador | Analista Financeiro | Usuário Comum |
|------|:-------------:|:-------------------:|:-------------:|
| Configurar APIs de mercado | ✅ | ❌ | ❌ |
| Configurar integração bancária | ✅ | ❌ | ❌ |
| Gerir planos e assinaturas | ✅ | ❌ | ❌ |
| Consultar logs de auditoria completos | ✅ | ❌ | ❌ |

---

## Regras de Negócio

### Projetos

- Um projeto só pode ser **editado** quando o status é **"Rascunho"**.
- A **exclusão** é do tipo *soft delete* e só é permitida se **não existir orçamento aprovado**.
- O analista financeiro só pode editar/excluir **os seus próprios projetos** (exceto administrador).
- Utilizadores comuns só visualizam projetos **explicitamente partilhados** com eles.

### Ingestão de Dados

- Cada item OPEX/CAPEX importado (manual ou Excel) deve gerar um **hash SHA-256** para rastreabilidade.
- Importação via Excel limitada a **máximo de 1000 linhas** por upload.
- O orçamento rastreável deve incluir **QR Code** para verificação em tempo real.
- Todas as alterações devem ser registadas no **audit trail**.

### Análise Financeira

- Indicadores: **60+ KPIs** incluindo VPL, TIR, ROI, ROE, EBITDA.
- Simulação Monte Carlo: entre **1.000 e 50.000 iterações**.
- Análise de sensibilidade: entre **3 e 10 variáveis**.
- Benchmarks comparados com **médias do setor africano**.

### Relatórios

| Tipo | Especificação |
|------|---------------|
| Internacional | PDF 10 secções, USD/EUR, PT/EN, com QR Code |
| BFA | Conforme Aviso BNA 10/2020, validação de documentos |
| BDA | Formulário 61 páginas, tabela de reembolsos automática |
| WhatsApp | Link temporário com validade de **7 dias** |

### Segurança

- Autenticação por **email e palavra-passe**.
- Recuperação de palavra-passe via **email**.
- Três perfis de acesso: `admin`, `financial`, `user`.
- Logs de acesso e auditoria para todas as ações sensíveis.

---

## Integrações Externas

| Integração | Finalidade | Módulo |
|------------|------------|--------|
| **Jumia** | Scraping de preços de fornecedores | Ingestão |
| **Jiji** | Scraping de preços de fornecedores | Ingestão |
| Outros marketplaces africanos | Scraping configurável pelo admin | Ingestão |
| **API BFA** | Submissão direta de relatórios | Relatórios |
| **API BDA** | Submissão direta de relatórios | Relatórios |
| **Email (SMTP)** | Envio de relatórios PDF | Relatórios |
| **WhatsApp** | Partilha de link temporário | Relatórios |

---

## Escopo de Implementação

### Frontend

- [ ] Dashboard com listagem e filtros de projetos
- [ ] Formulários de criação/edição de projetos
- [ ] Upload e preview de ficheiros Excel
- [ ] Interface de scraping com seleção de fornecedores
- [ ] Visualização de indicadores financeiros e gráficos
- [ ] Painel de Simulação Monte Carlo e Análise de Sensibilidade
- [ ] Kanban com drag-and-drop
- [ ] Chat em tempo real por projeto
- [ ] Geração e preview de relatórios PDF
- [ ] Painel de administração (utilizadores, APIs, planos)

### Backend

- [ ] API RESTful com autenticação JWT
- [ ] Sistema RBAC (Role-Based Access Control)
- [ ] Motor de cálculo financeiro (60+ indicadores)
- [ ] Engine Monte Carlo (1.000–50.000 iterações)
- [ ] Engine de análise de sensibilidade
- [ ] Serviço de scraping com filas assíncronas
- [ ] Geração de hashes SHA-256 e QR Codes
- [ ] Audit trail imutável
- [ ] Geração de PDF (Internacional, BFA, BDA)
- [ ] Soft delete e gestão de estados de projeto
- [ ] Gestão de planos e assinaturas

### Infraestrutura e Segurança

- [ ] Hash SHA-256 para rastreabilidade de dados
- [ ] QR Code em orçamentos e relatórios
- [ ] Logs de auditoria completos
- [ ] Links temporários com expiração (WhatsApp: 7 dias)
- [ ] Encriptação de credenciais de APIs bancárias

### Integrações

- [ ] Scraping: Jumia, Jiji e fontes configuráveis
- [ ] API BFA (Banco de Fomento Angola)
- [ ] API BDA (Banco de Desenvolvimento de Angola)
- [ ] Serviço de email (SMTP)
- [ ] API WhatsApp (link temporário)

---

## Referências

- Requisitos Funcionais: **RF001 a RF080**
- Checklist institucional: **BFA**
- Checklist institucional: **BDA**
- Normativa: **Aviso BNA 10/2020** (Banco Nacional de Angola)

---

## Resumo Quantitativo

| Elemento | Quantidade |
|----------|------------|
| Módulos funcionais | 7 |
| Casos de uso | 39 |
| Histórias do utilizador | 18 |
| Perfis de acesso | 3 |
| Indicadores financeiros | 60+ |
| Iterações Monte Carlo | 1.000 – 50.000 |
| Formatos de relatório | 3 (Internacional, BFA, BDA) |
| Requisitos funcionais | RF001 – RF080 |

---

**ViabilizA+ África** — Plataforma de Business Intelligence com Rastreabilidade Total

*Documento de especificação v2.0 — Junho 2026*
