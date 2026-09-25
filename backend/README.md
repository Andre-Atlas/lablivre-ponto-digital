# ⚙️ Ponto Digital — Backend API

Backend resiliente construído em **Python 3.11+** com **FastAPI**, **SQLAlchemy 2.0 (Async)** e **PostgreSQL**, estruturado segundo os princípios da **Arquitetura Hexagonal (Ports & Adapters)** para garantir independência de frameworks, alta testabilidade e separação estrita de regras de negócio.

---

## 🏛️ Estrutura de Diretórios

```
backend/
├── app/
│   ├── domain/           # Entidades puras, regras de negócio e interfaces (Ports)
│   ├── application/      # Casos de uso (Use Cases) e DTOs
│   ├── adapters/         # Adaptadores secundários (PostgreSQL, Google Sheets, Hashers)
│   └── api/              # Adaptadores primários (Rotas FastAPI, schemas de requisição/resposta)
├── migrations/           # Scripts de migração com Alembic
│   └── versions/         # Histórico versionado de migrações DDL
├── tests/
│   ├── unit/             # Testes unitários com mocks/fakes (rápidos, sem I/O)
│   └── integration/      # Testes de integração com banco de dados real
├── alembic.ini           # Configuração do Alembic
├── pyproject.toml        # Metadados do projeto e configurações de ferramentas (Ruff, Mypy)
└── requirements.txt      # Dependências de produção e desenvolvimento
```

---

## 📋 Pré-requisitos

- **Python 3.11** ou superior
- **Docker** e **Docker Compose** (recomendado para subir o PostgreSQL local)
- Gerenciador de pacotes **pip**

---

## 🛠️ Configuração e Execução Local

### 1. Criar e Ativar o Ambiente Virtual

```bash
cd backend
python3.11 -m venv .venv

# No Linux/macOS:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` conforme os parâmetros da sua máquina local.

### 4. Inicializar o Banco de Dados com Docker

```bash
docker run --name ponto-postgres -e POSTGRES_USER=ponto_user -e POSTGRES_PASSWORD=ponto_secret -e POSTGRES_DB=ponto_db -p 5432:5432 -d postgres:15-alpine
```

### 5. Executar as Migrações

```bash
alembic upgrade head
```

### 6. Iniciar o Servidor de Desenvolvimento

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

A documentação interativa estará acessível em:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔑 Variáveis de Ambiente (`.env`)

| Variável | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | String | `postgresql+asyncpg://ponto_user:ponto_secret@localhost:5432/ponto_db` | URI de conexão assíncrona ao PostgreSQL |
| `DATABASE_URL_SYNC` | String | `postgresql://ponto_user:ponto_secret@localhost:5432/ponto_db` | URI de conexão síncrona (utilizada pelo Alembic para migrações) |
| `SECRET_KEY` | String | *Obrigatório em prod* | Chave criptográfica para geração de tokens JWT |
| `ALGORITHM` | String | `HS256` | Algoritmo de assinatura do JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Inteiro | `1440` (24 horas) | Tempo de vida útil do token JWT em minutos |
| `ENVIRONMENT` | String | `development` | Ambiente de execução (`development`, `staging`, `production`) |
| `LOG_LEVEL` | String | `INFO` | Nível de verbosidade de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `GOOGLE_SHEETS_CREDENTIALS_JSON` | String / Caminho | `credentials.json` | Caminho ou JSON da Service Account do Google Cloud |
| `SHEET_ID_ALUNOS` | String | *Identificador da planilha* | ID da planilha Google Sheets de registros dos alunos |
| `SHEET_ID_STAFF` | String | *Identificador da planilha* | ID da planilha Google Sheets de registros do staff |
| `CORS_ORIGINS` | String | `http://localhost:5173,http://localhost:3000` | Lista de origens permitidas separadas por vírgula |

---

## 🗄️ Comandos de Migração (Alembic)

```bash
# Aplicar todas as migrações pendentes até a versão mais recente
alembic upgrade head

# Reverter a última migração aplicada
alembic downgrade -1

# Gerar uma nova revisão automática com base nas alterações das entidades SQLAlchemy
alembic revision --autogenerate -m "descricao_da_migracao"

# Visualizar o histórico de migrações aplicadas
alembic history --verbose

# Ver a versão atual do banco de dados
alembic current
```

---

## 🧪 Testes e Qualidade de Código

### Executar Suíte Completa de Testes
```bash
pytest
```

### Executar Testes com Relatório de Cobertura
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```
O relatório HTML detalhado será gerado em `htmlcov/index.html`.

### Executar Somente Testes Unitários
```bash
pytest tests/unit/
```

### Executar Somente Testes de Integração
```bash
pytest tests/integration/
```

### Linters e Checagem Estática
```bash
# Verificação de formatação e boas práticas com Ruff
ruff check app/ tests/

# Formatação automática de código
ruff format app/ tests/

# Checagem estrita de tipagem com Mypy
mypy app/
```
