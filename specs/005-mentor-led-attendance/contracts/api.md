# Phase 1 Contracts: API

Todos sob `/api/v1`, autenticação JWT (somente mentores). RBAC: mentor restrito às suas turmas (`mentor_turmas`); admin/super-admin acessam todas. Payloads validados por Pydantic.

## Autenticação (alteração)

- `POST /auth/login` — emite token **apenas** para mentores (STAFF/ADMIN/SUPER_ADMIN). ALUNO → 401/403.
- **Removidos**: registro/login de aluno; `POST /checkin/` e toda a rota de autofrequência.

## Lançamento de frequência (novo — `router_frequencia`)

- `GET /frequencia?turma={t}&data={YYYY-MM-DD}&turno={MANHA|TARDE}`
  - Retorna a lista de **alunos ATIVOS** da turma com o lançamento atual (status + se tem atestado). 403 se a turma não for do mentor.
- `POST /frequencia` (upsert idempotente)
  - Body: `{ turma, data, turno, lancamentos: [{ aluno_id, status: PRESENTE|FALTA }] }`
  - Cria/atualiza uma `Frequencia` por aluno. 403 fora de escopo; 400 se aluno não pertence à turma.
- `POST /frequencia/{id}/atestado` (multipart)
  - Anexa documento (PDF/JPEG/PNG, até 10 MB) a um lançamento de **FALTA** → status vira `JUSTIFICADO` (só aquele turno). 400 se o lançamento estiver `PRESENTE`.
- `GET /frequencia/{id}/atestado` — baixa o documento (restrito a mentores/admin).
- `DELETE /frequencia/{id}/atestado` — remove o atestado → volta a `FALTA`.

## Vínculo mentor–turma (admin — `router_admin`)

- `GET /admin/mentores/{user_id}/turmas` — lista turmas do mentor.
- `PUT /admin/mentores/{user_id}/turmas` — define o conjunto de turmas do mentor. Body: `{ turmas: [string] }` (cada uma deve existir em `config.turmas`).

## Status do aluno (admin/mentor — `router_admin`)

- `PUT /admin/alunos/{user_id}/status` — Body: `{ status: ATIVO|DESLIGADO }`. Desligar remove das listas ativas; reativar retorna.
- `GET /admin/usuarios` — passa a expor `status` dos alunos e a suportar filtro `?status=ATIVO|DESLIGADO`.

## Exportações (alteração — `router_admin`)

- `GET /admin/export/frequencia?...` — relatório baseado nos lançamentos (`Frequencia`), com `JUSTIFICADO` por atestado; alunos `DESLIGADO` aparecem apenas em relatórios históricos, marcados.
- Exportações de pontos do modelo antigo (auto-check-in) são removidas.

## Avaliações de LO (alteração)

- Endpoints existentes (`/admin/avaliacoes*`, `/admin/los*`) passam a: (a) listar apenas alunos `ATIVO`; (b) respeitar o escopo de turma do mentor (já restrito por turma hoje).

## Removidos

- `router_checkin` inteiro (autofrequência).
- Fluxo de atestado por período como entidade de UI (`router_certificates` deixa de ser exposto como aba; o armazenamento de documento passa para o lançamento). Registros antigos permanecem consultáveis por rota administrativa de histórico (se necessário).
