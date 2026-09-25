# 📚 Central de Documentação — Ponto Digital

Bem-vindo à base de conhecimento e documentação técnica do ecossistema **Ponto Digital**. Este repositório centraliza a arquitetura, decisões técnicas fundamentadas, contratos de API e procedimentos operacionais padrão.

---

## 🏛️ Registros de Decisões de Arquitetura (ADRs)

Todas as grandes decisões técnicas do projeto são documentadas e versionadas na pasta [`ADR/`](./ADR/):

| Código | Decisão | Status | Data | Resumo Executivo |
| :--- | :--- | :--- | :--- | :--- |
| [**ADR-001**](./ADR/ADR-001-arquitetura-hexagonal.md) | **Arquitetura Hexagonal no Backend** | `Aceita` | 2026-09-24 | Adoção do padrão Ports & Adapters no FastAPI, garantindo regras de domínio puras e desacoplamento de I/O e bancos de dados. |
| [**ADR-002**](./ADR/ADR-002-flet-client.md) | **Flet como Framework de UI do Client Desktop** | `Aceita` | 2026-09-24 | Utilização do Flutter runtime encapsulado em Python (Flet) para distribuição multiplataforma consistente com PyInstaller. |
| [**ADR-003**](./ADR/ADR-003-google-sheets-raw.md) | **Google Sheets como Camada de Dados Raw** | `Aceita` | 2026-09-24 | Exportação automatizada de dados brutos para planilhas isoladas via Service Account, consumidas pelo RH via `IMPORTRANGE`. |

---

## 🔌 Especificações de API & Contratos

Documentação das rotas, payloads, schemas de validação e códigos de resposta:

- [**Guia de Autenticação & Sessão**](./api/auth.md) *(Em elaboração)*: Fluxo JWT, renovação de tokens e cabeçalhos de autorização.
- [**Contratos de Registro de Ponto**](./api/checkin.md) *(Em elaboração)*: Endpoints para registro de batida, sincronização offline em lote e consulta de espelho.
- [**Especificação OpenAPI / Swagger**](../backend/README.md#6-iniciar-o-servidor-de-desenvolvimento): Acesse `/docs` ou `/redoc` na instância da API em execução para navegar pelo schema interativo.

---

## ⚙️ Guias de Instalação e Ambiente

Manuais para configuração rápida dos ambientes de desenvolvimento e teste:

- [**Configuração de Ambiente Local**](./setup/local-development.md) *(Em elaboração)*: Passo a passo para configurar simultaneamente Backend, Client e Dashboard.
- [**Guia de Integração com Google Cloud & Sheets API**](./setup/google-sheets-setup.md) *(Em elaboração)*: Criação da Service Account no GCP, atribuição de papéis e compartilhamento das planilhas.
- [**Configuração do PostgreSQL Local via Docker**](./setup/database-docker.md) *(Em elaboração)*: Provisionamento e aplicação de migrações locais.

---

## 🔄 Fluxo de Desenvolvimento e Governança

Para entender os papéis do squad de desenvolvimento, atribuição de responsabilidades e as regras invioláveis de qualidade, consulte:
👉 [**Diretrizes e Governança do Squad (AGENTS.md)**](../AGENTS.md)
