---
description: "Task list for Frequência lançada por mentores"
---

# Tasks: Frequência lançada por mentores

**Input**: Design documents from `/specs/005-mentor-led-attendance/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md
**Tests**: Obrigatórios (Constituição — Princípio V: TDD, cobertura ≥80%; SC-002/003/007).

**Paths**: backend em `backend/`, frontend em `web_admin/`.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: paralelizável (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1 (lançamento), US2 (fim autofrequência/login), US3 (mentor–turma), US4 (status do aluno)

---

## Phase 1: Setup

- [x] T001 Confirmar baseline de migração (único head Alembic) em `backend/migrations/` e criar branch de trabalho a partir da base integrada.
- [x] T002 [P] Levantar inventário dos pontos a remover (autofrequência/login de aluno/aba Atestados) com `rg`: `router_checkin`, `/checkin`, `Checkin.tsx`, `AtestadosPage`, registro/login de ALUNO — anotar em um checklist local para as fases US1/US2.

## Phase 2: Foundational (BLOQUEIA todas as histórias)

- [x] T003 [P] Adicionar enums `StatusAluno` (ATIVO/DESLIGADO) e `StatusFrequencia` (PRESENTE/FALTA/JUSTIFICADO) em `backend/app/domain/enums.py`.
- [x] T004 Adicionar ORM em `backend/app/adapters/persistence/orm_models.py`: coluna `status` em `User` (default ATIVO), tabela `mentor_turmas` (user_id, turma, único) e tabela `frequencias` (aluno_id, turma, data, turno, status, mentor_id, atestado_documento/filename/content_type, observacao, timestamps; único por aluno/data/turno).
- [x] T005 Criar migração Alembic em `backend/migrations/versions/` que cria `mentor_turmas`, `frequencias` e `users.status`, e **descarta** os dados de `checkins` (modelo de autofrequência). Preserva atestados/avaliações.
- [x] T006 [P] Adicionar dataclasses/validações de domínio em `backend/app/domain/models.py`: `Frequencia` + regras de transição de status e validação de atestado-por-turno.
- [x] T007 [P] Criar porta `backend/app/domain/ports/frequencia_repository.py` (interface do repositório de frequência).
- [x] T008 Atualizar `backend/tests/conftest.py` para criar as novas tabelas no schema de teste (sqlite) e remover dependências de `checkins` nos fixtures.

**Checkpoint**: schema novo aplica em sqlite; domínio compila; nenhuma lógica de produto ainda.

---

## Phase 3: User Story 1 — Mentor lança a frequência (Priority: P1) 🎯 MVP

**Goal**: Mentor lança Presente/Falta por turma/data/turno e atrela atestado por turno; sem aba de Atestados.
**Independent Test**: lançar frequência de uma turma, reabrir e ver persistido; marcar Falta + anexar atestado → Justificado.

- [x] T009 [P] [US1] Teste de domínio em `backend/tests/unit/test_frequencia_domain.py`: transições PRESENTE↔FALTA, FALTA→JUSTIFICADO ao anexar atestado, atestado proibido em PRESENTE.
- [x] T010 [P] [US1] Teste de integração em `backend/tests/integration/test_frequencia_api.py`: upsert idempotente por (aluno,data,turno); anexar/baixar/remover atestado; 400 atestado em Presente.
- [x] T011 [US1] Implementar `backend/app/adapters/persistence/frequencia_repo_impl.py` (upsert por aluno/data/turno, consulta por turma/data/turno, anexar/remover atestado).
- [x] T012 [US1] Implementar `backend/app/application/frequencia_use_case.py` (lançar lista, atrelar/remover atestado, aplicar transições e regras).
- [x] T013 [US1] Criar `backend/app/api/schemas/frequencia_schemas.py` (lançamento, item, resposta com status + flag de atestado).
- [x] T014 [US1] Criar `backend/app/api/v1/router_frequencia.py` com `GET /frequencia`, `POST /frequencia`, `POST/GET/DELETE /frequencia/{id}/atestado`; registrar em `backend/app/main.py`.
- [x] T015 [P] [US1] Cliente de API em `web_admin/src/services/api.ts`: `getFrequencia`, `lancarFrequencia`, `anexarAtestado`, `removerAtestado`, `baixarAtestado`.
- [x] T016 [US1] Criar `web_admin/src/pages/admin/FrequenciaPage.tsx`: seletor turma/data/turno, lista de alunos ATIVOS, marcação individual Presente/Falta, anexo de atestado por aluno em Falta, salvar (upsert), estados loading/empty/erro.
- [x] T017 [US1] Remover a aba Atestados: deletar `web_admin/src/pages/admin/AtestadosPage.tsx`, rota em `web_admin/src/App.tsx` e item "Atestados" em `web_admin/src/components/AdminNavbar.tsx`; adicionar item/rota "Frequência".
- [x] T018 [US1] Definir o destino do atestado antigo (feature 001): manter `MedicalCertificate`/`CertificateDay` **apenas como histórico somente-leitura** (sem aba, sem novas criações por período); o novo documento de atestado é armazenado em `frequencias.atestado_documento`, **sem consolidar** os dois acervos (decisão explícita — ver A2 da análise). Remover a exposição de `router_certificates` como aba e limpar imports órfãos em `backend/app/main.py` e `web_admin/src`.
- [x] T019 [US1] E2E em `web_admin/tests/e2e/frequencia.spec.ts`: mentor lança turma, reabre e confere; Falta + atestado → Justificado; axe sem violações sérias.

**Checkpoint (US1 = MVP)**: mentor lança frequência com atestado por turno; aba Atestados removida; testes verdes.

---

## Phase 4: User Story 2 — Fim da autofrequência e do login de aluno (Priority: P1)

**Goal**: Remover auto-check-in e qualquer autenticação de aluno; só mentores entram.
**Independent Test**: não há tela/rota de bater ponto; aluno não loga; mentor loga normalmente.

- [x] T020 [P] [US2] Teste de integração em `backend/tests/integration/test_auth_mentor_only.py`: login de ALUNO → 401/403; login de mentor → 200; rota de check-in inexistente (404).
- [x] T021 [US2] Remover autofrequência no backend: deletar `backend/app/api/v1/router_checkin.py` e seu registro em `backend/app/main.py`; remover repos/usos específicos de check-in não reaproveitados.
- [x] T022 [US2] Ajustar `backend/app/api/v1/router_auth.py`: remover registro/login de ALUNO; `login` emite token apenas para mentores (STAFF/ADMIN/SUPER_ADMIN).
- [x] T023 [US2] Remover testes antigos de auto-check-in em `backend/tests/` que não se aplicam mais (ou convertê-los para asserts de ausência).
- [x] T024 [US2] Frontend: deletar `web_admin/src/pages/Checkin.tsx`, remover a rota `/checkin` e a ramificação de aluno em `web_admin/src/App.tsx`; remover do `web_admin/src/pages/Login.tsx` o modo "Criar conta"/registro e qualquer login de aluno.
- [x] T025 [P] [US2] Limpar `web_admin/src/services/api.ts`: remover chamadas de check-in e de autorregistro de aluno.

**Checkpoint (US2)**: zero caminhos de autofrequência/login de aluno; só mentores autenticam.

---

## Phase 5: User Story 3 — Vínculo mentor–turma e RBAC (Priority: P2)

**Goal**: Mentor atrelado a 1+ turmas; só acessa/lança nas suas; admin vê todas.
**Independent Test**: mentor de 1 turma recebe 403 em outra; mentor de 2 alterna sem misturar; admin vê tudo.

- [ ] T026 [P] [US3] Teste de integração em `backend/tests/integration/test_mentor_turma_rbac.py`: mentor fora de escopo → 403 em frequência/avaliação; admin acessa todas; set/get de turmas do mentor; **regressão FR-010**: cadastro de aluno exige **exatamente uma** turma já cadastrada (rejeita sem turma / turma inexistente).
- [ ] T027 [US3] Endpoints em `backend/app/api/v1/router_admin.py`: `GET/PUT /admin/mentores/{id}/turmas` (valida contra `config.turmas`).
- [ ] T028 [US3] Implementar guard/dependência de RBAC por turma reutilizável e aplicá-la em `router_frequencia` e nos endpoints de avaliação (`router_evaluations`/avaliações em `router_admin`).
- [ ] T029 [P] [US3] Frontend: em `web_admin/src/pages/admin/PessoasPage.tsx` (ou nova seção em Cadastro), permitir atribuir turmas a um mentor; `web_admin/src/services/api.ts` com `getMentorTurmas`/`setMentorTurmas`.
- [ ] T030 [US3] Escopar a UI do mentor: `FrequenciaPage`/avaliações só listam as turmas do mentor logado (admin vê todas).

**Checkpoint (US3)**: segregação por turma garantida no servidor e refletida na UI.

---

## Phase 6: User Story 4 — Status do aluno (Ativo/Desligado) (Priority: P2)

**Goal**: Desligar/reativar aluno; Desligado fora das listas ativas, presente em exportações históricas.
**Independent Test**: desligar some das listas de lançamento/avaliação; aparece em export histórico marcado; reativar volta.

- [ ] T031 [P] [US4] Teste de integração em `backend/tests/integration/test_status_aluno.py`: desligar remove das listas ativas; export histórico inclui Desligado marcado; reativar restaura.
- [ ] T032 [US4] Endpoint `PUT /admin/alunos/{id}/status` em `backend/app/api/v1/router_admin.py`; `GET /admin/usuarios` passa a expor `status` e aceitar `?status=`.
- [ ] T033 [US4] Filtrar alunos ATIVOS nas listas ativas: lançamento de frequência, avaliação de LOs e dashboards (`router_frequencia`, avaliações, dashboard).
- [ ] T034 [US4] Exportações (`router_admin`): relatório de frequência baseado em `Frequencia`; incluir alunos Desligados apenas em relatórios históricos, marcados; remover exportações de pontos do modelo antigo.
- [ ] T035 [P] [US4] Frontend: em `web_admin/src/pages/admin/PessoasPage.tsx`, exibir e alternar status Ativo/Desligado do aluno; `web_admin/src/services/api.ts` com `setAlunoStatus`.

**Checkpoint (US4)**: status aplicado em listas ativas e exportações.

---

## Phase 7: Polish & Cross-Cutting

- [ ] T036 [P] Rodar suíte backend com cobertura (`pytest --cov`) e garantir ≥80%; corrigir lacunas.
- [ ] T037 [P] Rodar frontend `npm run build` + `npm run lint` + E2E/axe; corrigir.
- [ ] T038 [P] Guards: `rg` sem resíduos de `router_checkin`/`Checkin`/`AtestadosPage`/registro de ALUNO em `backend/app` e `web_admin/src`.
- [ ] T039 Atualizar documentação (Princípio VI): OpenAPI/Swagger, `README.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md` — novo modelo de frequência, remoção de autofrequência/login de aluno, mentor–turma, status, atestado-por-turno, aposentadoria do `desktop_app`.
- [ ] T040 Verificação final via `quickstart.md` (cenários 1–6) em stack ativo.

---

## Dependencies & order
- **Setup (T001–T002)** → **Foundational (T003–T008)** bloqueiam tudo.
- **US1 (T009–T019)** = MVP; **US2 (T020–T025)** pode correr em paralelo após Foundational (arquivos majoritariamente distintos; coordenar `Login.tsx`/`App.tsx`/`api.ts` para evitar conflito com US1).
- **US3 (T026–T030)** depende de Foundational + `router_frequencia` (US1) existir para aplicar o guard.
- **US4 (T031–T035)** depende de Foundational + listas de US1/avaliações.
- **Polish (T036–T040)** por último.

## Parallel opportunities
- T003/T006/T007 `[P]`; T009/T010 `[P]`; testes `[P]` de cada história; T015/T025/T029/T035 tocam `api.ts` (NÃO paralelizar entre si — mesmo arquivo).

## MVP scope
**US1 (via Setup + Foundational)** entrega o valor central: mentor lança frequência com atestado por turno e a aba de Atestados some. US2 remove o fluxo antigo; US3/US4 endurecem escopo e status.
