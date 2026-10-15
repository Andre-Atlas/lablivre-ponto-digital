# Implementation Plan: Frequência lançada por mentores

**Branch**: `005-mentor-led-attendance` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-mentor-led-attendance/spec.md`

## Summary

Inverter o modelo de frequência: a presença passa a ser **lançada pelos mentores** (não mais auto-registrada pelos alunos). Remover a autofrequência e o login de aluno; formalizar os vínculos **mentor N–N turma** e **aluno 1–1 turma**; introduzir **status do aluno** (Ativo/Desligado); e atrelar **atestados no próprio lançamento** (por turno), eliminando a tela separada de Atestados. Mantém a arquitetura hexagonal e o stack atual.

Abordagem técnica: novo agregado de domínio `Frequencia` (lançamento por aluno/data/turno, com mentor autor e documento de atestado opcional por turno) substituindo o cálculo de falta a partir de `Checkin`; tabela de junção `mentor_turmas`; coluna `status` para alunos; RBAC de mentor restrito às suas turmas. No frontend, a tela de Check-in do aluno e a página de Atestados são removidas; surge a tela de **Lançamento de frequência**. Migração Alembic dedicada que **descarta** os check-ins antigos e preserva atestados/avaliações.

## Technical Context

**Language/Version**: Python 3.x (backend), TypeScript/React 19 (frontend) — inalterados.

**Primary Dependencies**: FastAPI, SQLAlchemy 2 async (asyncpg), Alembic, Pydantic, python-jose/bcrypt (backend); React 19 + Vite + Tailwind v4 + react-router (frontend). **Nenhuma dependência nova.**

**Storage**: PostgreSQL (prod) / sqlite (dev/testes). Novas tabelas: `mentor_turmas`, `frequencias`. Alteração: `users.status` (alunos). Remoção lógica/descarte: dados de `checkins` do modelo de autofrequência.

**Testing**: pytest (unit + integração, ≥80% cobertura backend); Playwright E2E + axe no frontend.

**Target Platform**: Web (navegadores modernos). O cliente desktop de autofrequência (`desktop_app`) é **aposentado** (fora de escopo de manutenção nesta feature).

**Project Type**: Web app — backend (`backend/`) + frontend (`web_admin/`).

**Performance Goals**: lançar a frequência de uma turma (todos os alunos de um turno) em < 2 min; endpoints de lançamento idempotentes (upsert por turma/data/turno).

**Constraints**: RBAC — mentor só acessa dados das suas turmas; alunos sem credenciais; Desligados fora das listas ativas mas presentes em exportações históricas; atestado cobre apenas o turno marcado; preservar atestados/avaliações, **descartar** check-ins antigos.

**Scale/Scope**: dezenas a centenas de alunos por turma; poucas turmas; poucos mentores por turma.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Stack Stability | ✅ PASS | Sem novo stack. Novas tabelas/endpoints e remoção de fluxos dentro do FastAPI/SQLAlchemy/React existentes. |
| II. Contract-First & Decoupled | ✅ PASS | Novos contratos de API (lançamento de frequência, vínculo mentor–turma, status do aluno, atestado-no-lançamento) definidos em `contracts/` antes da implementação. |
| III. Async & Stateless | ✅ PASS | Todos os novos acessos a banco em async; sem estado em disco local. |
| IV. Security & RBAC | ✅ PASS (reforça) | Remove autenticação de aluno; adiciona escopo por turma para mentores; valida vínculo mentor↔turma no servidor em cada operação. |
| V. Test-First Quality Gates | ✅ PASS | TDD para lançamento, RBAC por turma, filtro por status, atestado-por-turno; remover testes de auto-check-in; cobertura ≥80%. |
| VI. Impeccable UX & Living Docs | ✅ PASS | Nova tela de lançamento (estados loading/empty/erro/foco), remoção da tela de aluno e da aba Atestados; docs (README/ARCHITECTURE/CHANGELOG/OpenAPI) atualizados na mesma mudança. |

**Gate result**: PASS com **um desvio registrado** (descarte de dados históricos de check-in — aprovado pelo usuário em `/speckit-clarify`). Prosseguir.

## Project Structure

### Documentation (this feature)

```text
specs/005-mentor-led-attendance/
├── plan.md              # Este arquivo
├── research.md          # Fase 0 — decisões de modelo e migração
├── data-model.md        # Fase 1 — entidades, campos, relações, transições
├── quickstart.md        # Fase 1 — roteiro de validação
├── contracts/           # Fase 1 — contratos de API
│   └── api.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── domain/
│   │   ├── models.py                 # + Frequencia, StatusFrequencia; status do aluno; helpers de turno
│   │   ├── enums.py                  # + StatusAluno (ATIVO/DESLIGADO), StatusFrequencia (PRESENTE/FALTA/JUSTIFICADO)
│   │   └── ports/
│   │       └── frequencia_repository.py        # NOVO (porta)
│   ├── application/
│   │   └── frequencia_use_case.py              # NOVO (lançar/consultar frequência, atrelar atestado por turno)
│   ├── adapters/persistence/
│   │   ├── orm_models.py             # + mentor_turmas (M2M), frequencias; users.status; (desativar checkin no fluxo)
│   │   └── frequencia_repo_impl.py             # NOVO
│   ├── api/
│   │   ├── schemas/frequencia_schemas.py       # NOVO
│   │   └── v1/
│   │       ├── router_frequencia.py            # NOVO (lançamento, consulta, atrelar atestado)
│   │       ├── router_admin.py                 # mentor–turma (M2M), status do aluno; exportações por lançamento
│   │       ├── router_auth.py                  # remover register/login de ALUNO
│   │       ├── router_checkin.py               # REMOVER (autofrequência)
│   │       └── router_certificates.py          # substituído por atestado-no-lançamento (doc por turno)
│   └── main.py                       # remover router_checkin; registrar router_frequencia
├── migrations/versions/*             # NOVA migração: mentor_turmas, frequencias, users.status; DESCARTAR checkins antigos
└── tests/                            # + testes de frequência/RBAC/status; - testes de auto-check-in

web_admin/src/
├── App.tsx                           # remover rota/guarda de aluno (/checkin); home de mentor
├── pages/
│   ├── Checkin.tsx                   # REMOVER (tela do aluno)
│   └── admin/
│       ├── FrequenciaPage.tsx        # NOVO — lançamento por turma/data/turno + atrelar atestado
│       ├── AtestadosPage.tsx         # REMOVER (vira parte do lançamento)
│       └── PessoasPage.tsx           # + status Ativo/Desligado; vínculo mentor–turma
├── components/AdminNavbar.tsx        # remover "Atestados"; adicionar "Frequência"
└── services/api.ts                   # + frequência; remover check-in/auto-registro; atestado via lançamento
```

**Structure Decision**: Mantém a separação hexagonal (domínio → caso de uso → adaptador → router) já usada nas features 001/002. A frequência vira um agregado próprio (`Frequencia`) com seu repositório e caso de uso; o vínculo mentor–turma é uma tabela de junção; o status do aluno é um campo no `User`. Remoções (auto-check-in, login de aluno, aba Atestados) são parte do escopo.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Migração **destrutiva** (descarta `checkins` antigos) — tensão com "preservar histórico" (Princípio VI / boas práticas de dados) | O usuário decidiu explicitamente (`/speckit-clarify`) descartar o histórico de autofrequência, que deixa de ter significado no novo modelo. Atestados e avaliações são preservados. | Migrar check-ins antigos para `frequencias` foi rejeitado (semântica diferente — auto-registro ≠ lançamento do mentor — gera dados enganosos); manter as duas tabelas foi rejeitado por confundir a fonte de verdade. |
| Substituir o modelo de atestado por período (feature 001) por **atestado por turno** no lançamento | Decisão de produto em `/speckit-clarify`: atestado é atrelado no lançamento e cobre só o turno. | Manter atestado por período + aba separada foi rejeitado pelo usuário (quer tudo no fluxo de lançamento). Registros de atestado já existentes são preservados como histórico. |
| Remover um cliente inteiro (`desktop_app` de autofrequência) | Sem autofrequência, o cliente do aluno perde função. | Mantê-lo ativo induziria usuários a um fluxo que não existe mais. Fica aposentado/fora de escopo de manutenção. |
