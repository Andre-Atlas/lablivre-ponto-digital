---

description: "Task list for Weekly Learning-Outcome Evaluation"
---

# Tasks: Weekly Learning-Outcome Evaluation

**Input**: Design documents from `/specs/002-weekly-lo-evaluation/`

**Prerequisites**: plan.md ✅, spec.md ✅ (clarified 2026-10-13), research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: INCLUDED — the project constitution (Principle V, Test-First, NON-NEGOTIABLE) mandates
TDD. Test tasks are written first within each phase and MUST fail before the implementation tasks
that satisfy them.

**Organization**: Tasks are grouped by user story (US1–US4 from spec.md) so each story is an
independently testable, deployable increment.

**Clarifications applied** (2026-10-13): mentors are STAFF/ADMIN scoped to their single
`turma_ou_equipe` (FR-006); co-evaluation = one evaluation per student/week, last level wins per LO
with both mentors' comments kept; all evaluation data is staff-only in v1 (FR-014). No new
dependencies.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3 / US4 (Setup, Foundational, Polish carry no story label)
- Exact file paths are included in every task.

## Path Conventions

Decoupled web app (per plan.md): backend hexagon under `backend/app/` with tests in
`backend/tests/`; frontend SPA under `web_admin/src/`. No new top-level projects.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature configuration conventions (no new dependencies needed).

- [x] T001 Define level + program-config constants in `backend/app/domain/models.py` (level range 1–4; default `NUM_SEMANAS = 12`) and document the `config` keys `lo_eval_data_inicio` / `lo_eval_num_semanas` as the program-config source of truth.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared domain, persistence, ports, schemas, auth, and router skeleton that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T002 Add an autouse session-scoped fixture to `backend/tests/conftest.py` that runs `Base.metadata.create_all` so new tables exist for the test DB.
- [x] T003 Write FAILING unit tests in `backend/tests/unit/test_evaluation_domain.py` for: `semana_de(data, inicio)` and current-week clamping; pure pre-fill selection (most recent prior-week level per LO); regression detection (flag only when a comparable prior level exists); level validation (reject ≠ 1–4).
- [x] T004 [P] Add domain dataclasses `LearningOutcome`, `WeeklyEvaluation`, `EvaluationLevel`, `EvaluationComment` to `backend/app/domain/models.py`.
- [x] T005 Implement domain functions in `backend/app/domain/models.py`: `semana_de`/current-week, pure pre-fill selector, and regression detector — making T003 pass (depends on T004).
- [x] T006 [P] Add ORM models `LearningOutcome`, `WeeklyEvaluation` (unique `(user_id, semana)`), `EvaluationLevel` (unique `(evaluation_id, lo_id)`, lo FK `RESTRICT`), `EvaluationComment` (unique `(evaluation_id, mentor_id)`) to `backend/app/adapters/persistence/orm_models.py` per data-model.md.
- [x] T007 [P] Define ports `LearningOutcomeRepository` and `EvaluationRepository` (ABCs) in `backend/app/domain/ports/learning_outcome_repository.py` and `backend/app/domain/ports/evaluation_repository.py`.
- [x] T008 Create the Alembic migration creating the 4 tables (FKs, indexes, unique constraints) in `backend/migrations/versions/`, chained to current head `a02dab1dca18` (depends on T006).
- [x] T009 Implement `LearningOutcomeRepositoryImpl` and `EvaluationRepositoryImpl` (all port methods, async SQLAlchemy; evaluation repo supports upsert of levels and per-mentor comment) in `backend/app/adapters/persistence/learning_outcome_repo_impl.py` and `backend/app/adapters/persistence/evaluation_repo_impl.py` (depends on T006, T007).
- [x] T010 [P] Create Pydantic schemas matching `contracts/weekly-lo-evaluation.openapi.yaml` in `backend/app/api/schemas/evaluation_schemas.py`.
- [x] T011 Add a `require_mentor` dependency (allows `tipo == STAFF` or `role` in ADMIN/SUPER_ADMIN; returns the `User`) in `backend/app/api/middleware/auth_dependencies.py`, and a program-config reader (reads `lo_eval_data_inicio`/`lo_eval_num_semanas` from the existing `config` table, computes current week).
- [x] T012 Scaffold `backend/app/api/v1/router_evaluations.py` (prefixes `/admin/los` and `/admin/avaliacoes`), register it in `backend/app/main.py`, and create `LOCatalogUseCase` + `EvaluationUseCase` skeletons in `backend/app/application/lo_catalog_use_case.py` and `backend/app/application/evaluation_use_case.py` (depends on T009, T010, T011).

**Checkpoint**: Data layer, ports, schemas, auth, and router are in place; story implementation can begin.

---

## Phase 3: User Story 1 - Mentor records a student's weekly evaluation (Priority: P1) 🎯 MVP

**Goal**: A mentor submits/updates a student's weekly levels (1–4 per LO) + comment, with the form pre-filled from the student's last known levels.

**Independent Test**: With a seeded LO catalog and a student, submit week-3 levels; reopening week 3 shows them; week-4 pre-fill reflects them; invalid level/LO/week and cross-turma attempts are rejected.

### Tests for User Story 1 (write first, must FAIL) ⚠️

- [x] T013 [US1] Write FAILING integration tests in `backend/tests/integration/test_evaluation_api.py`: submit happy path (200 + persisted levels attributed to mentor + comment); re-open via GET returns them; prefill returns prior-week levels; validation (level ≠ 1–4 / inactive or unknown LO / week out of program range → 400); turma scoping (mentor of another turma → 403); co-evaluation (second mentor's submit → last level wins, both comments kept); RBAC (ALUNO → 403, missing token → 401); student not found → 404.

### Implementation for User Story 1

- [x] T014 [US1] Implement `EvaluationUseCase.registrar` (validate week-in-range, active LO, level 1–4, mentor turma == student turma; upsert levels last-write-wins with mentor attribution; replace caller's comment only) in `backend/app/application/evaluation_use_case.py` (depends on T012).
- [x] T015 [US1] Implement `EvaluationUseCase.obter` and `EvaluationUseCase.prefill` in `backend/app/application/evaluation_use_case.py`.
- [x] T016 [US1] Implement endpoints `POST /admin/avaliacoes`, `GET /admin/avaliacoes`, `GET /admin/avaliacoes/prefill`, `GET /admin/avaliacoes/config` (all `require_mentor` + turma check) in `backend/app/api/v1/router_evaluations.py` (depends on T014, T015).
- [x] T017 [P] [US1] Add client calls (`getProgramConfig`, `getPrefill`, `getEvaluation`, `submitEvaluation`) to `web_admin/src/services/api.ts`.
- [x] T018 [US1] Add `web_admin/src/components/AvaliacoesPanel.tsx` (student + week pickers, LO rows pre-filled with prior levels, 1–4 inputs, comment; loading/empty/error states; Light/Dark; keyboard-accessible) (depends on T017).
- [x] T019 [US1] Wire an "Avaliações LOs" entry point into `web_admin/src/pages/Dashboard.tsx` that opens `AvaliacoesPanel` (depends on T018).
- [x] T020 [US1] Add Playwright E2E `web_admin/tests/e2e/avaliacoes.spec.ts`: mentor logs in, opens the panel, evaluates a student for a week, re-opens and sees saved levels.

**Checkpoint**: MVP — mentors can capture weekly evaluations with pre-fill, end-to-end.

---

## Phase 4: User Story 2 - Administrator manages the LO catalog (Priority: P2)

**Goal**: Admins add/edit/deactivate learning outcomes; forms/dashboards use the active catalog; history preserved.

**Independent Test**: Admin adds an LO and deactivates another; new lists reflect the change while past evaluations referencing the deactivated LO remain intact; non-admin writes are rejected.

### Tests for User Story 2 (write first, must FAIL) ⚠️

- [x] T021 [US2] Write FAILING integration tests in `backend/tests/integration/test_lo_catalog_api.py`: create/list/update/deactivate; `incluir_inativos` filter; duplicate `numero` → 400; RBAC (STAFF/ALUNO create → 403; admin allowed); deactivation hides LO from active list but a historical evaluation still references it.

### Implementation for User Story 2

- [x] T022 [US2] Implement `LOCatalogUseCase` (create, list with/without inactive, update/deactivate; duplicate-numero guard) in `backend/app/application/lo_catalog_use_case.py`.
- [x] T023 [US2] Implement endpoints `GET /admin/los` (`require_mentor`), `POST /admin/los` and `PUT /admin/los/{lo_id}` (`require_admin`) in `backend/app/api/v1/router_evaluations.py` (depends on T022).
- [x] T024 [P] [US2] Add client calls (`listLearningOutcomes`, `createLearningOutcome`, `updateLearningOutcome`) to `web_admin/src/services/api.ts`.
- [x] T025 [US2] Add `web_admin/src/components/LOCatalogPanel.tsx` (admin-only list + add/edit/deactivate) and wire an entry point into `web_admin/src/pages/Dashboard.tsx` (depends on T024).

**Checkpoint**: US1 + US2 work independently; the evaluation form uses the managed active catalog.

---

## Phase 5: User Story 3 - Weekly dashboard for a turma (Priority: P2)

**Goal**: Per-turma/week dashboard: assessed vs pending, per-mentor counts, level heatmap per LO, regressions vs prior week.

**Independent Test**: With several students evaluated (one pending, one regressed), the dashboard shows correct counts, per-mentor tallies, heatmap, and flags the regression.

### Tests for User Story 3 (write first, must FAIL) ⚠️

- [x] T026 [US3] Write FAILING integration tests in `backend/tests/integration/test_dashboard_api.py`: assessed/pending split (incl. pending identities); per-mentor counts across two mentors; heatmap level counts per LO; regression flagged when week-N level < most recent prior comparable level, and NOT flagged when no comparable prior exists; RBAC (ALUNO → 403).

### Implementation for User Story 3

- [x] T027 [US3] Implement `EvaluationUseCase.dashboard(turma, semana)` (assessed/pending, por_mentor, heatmap, regressions) in `backend/app/application/evaluation_use_case.py`.
- [x] T028 [US3] Implement endpoint `GET /admin/avaliacoes/dashboard` (`require_mentor`) in `backend/app/api/v1/router_evaluations.py` (depends on T027).
- [x] T029 [P] [US3] Add `getDashboard` client call to `web_admin/src/services/api.ts`.
- [x] T030 [US3] Add `web_admin/src/components/LODashboardPanel.tsx` (counts, per-mentor, heatmap grid, regressions list; empty/loading states) and wire an entry point into `web_admin/src/pages/Dashboard.tsx` (depends on T029).

**Checkpoint**: US1–US3 independently functional; captured data is visible and analyzed.

---

## Phase 6: User Story 4 - Export a weekly report (Priority: P3)

**Goal**: Export per-student levels + comments for a turma/week via the existing CSV/Excel engine; pending students marked.

**Independent Test**: For a week with evaluations, the export lists each student with per-LO levels and comments; un-evaluated students appear as pending.

### Tests for User Story 4 (write first, must FAIL) ⚠️

- [x] T031 [US4] Write FAILING integration tests in `backend/tests/integration/test_evaluation_export.py`: CSV and Excel each contain a row per turma student with a column per active LO (level or blank) and the week's comments; pending students marked; RBAC (`require_mentor`).

### Implementation for User Story 4

- [x] T032 [US4] Implement `EvaluationUseCase.dados_relatorio(turma, semana)` (per-student levels per active LO + comments + pending flag) in `backend/app/application/evaluation_use_case.py`.
- [x] T033 [US4] Implement endpoint `GET /admin/avaliacoes/export?format=csv|excel` (`require_mentor`, `StreamingResponse` via openpyxl/`csv`) in `backend/app/api/v1/router_evaluations.py` (depends on T032).
- [x] T034 [P] [US4] Add `exportWeeklyReport` (blob download) client call to `web_admin/src/services/api.ts` and an export button in the dashboard panel (`web_admin/src/components/LODashboardPanel.tsx`).

**Checkpoint**: All four stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, verification, hardening (constitution V & VI).

- [x] T035 [P] Align endpoint summaries/docstrings in `backend/app/api/v1/router_evaluations.py` with `contracts/weekly-lo-evaluation.openapi.yaml` so the generated OpenAPI (`/docs`) matches.
- [x] T036 [P] Update `README.md`, `docs/ARCHITECTURE.md`, and `CHANGELOG.md` to document the weekly LO evaluation feature (catalog, evaluation, dashboard, export; staff-only; single-turma mentor) — Principle VI.
- [x] T037 Run `pytest --cov=app --cov-report=term-missing` from `backend/` and close gaps until new modules reach ≥80% coverage.
- [ ] T038 Execute `quickstart.md` Scenarios 1–6 against the docker-compose stack and confirm expected outcomes.
- [x] T039 [P] Security pass: confirm catalog writes are admin-only, all evaluation endpoints are behind `require_mentor` with server-side turma scoping, students have no access, and no secrets were added (Principle IV).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup — **BLOCKS all user stories**.
- **User Stories (Phases 3–6)**: depend on Foundational; then proceed in priority order (P1 → P2 → P2 → P3) or in parallel if staffed.
- **Polish (Phase 7)**: after the desired stories are complete.

### User Story Dependencies

- **US1 (P1)**: depends only on Foundational; seeds its own LOs in tests. MVP.
- **US2 (P2)**: depends on Foundational; independent (manages the catalog US1 consumes, but testable alone).
- **US3 (P2)**: depends on Foundational; reads US1 data but testable with seeded evaluations.
- **US4 (P3)**: depends on Foundational; reads US1 data but testable with seeded evaluations.

### Within Each User Story

- Test task(s) first and failing → use case → endpoint → frontend client → frontend UI/E2E.
- Models before services; services before endpoints; backend before the UI that calls it.

### Parallel Opportunities

- Foundational: T004, T006, T007, T010 [P] (distinct files); T005 waits on T004, T008 on T006, T009 on T006+T007, T012 on T009+T010+T011.
- Per story: the `api.ts` client task ([P]) runs alongside backend tasks (different file) — T017, T024, T029, T034.
- ⚠️ Shared files to serialize across stories: `web_admin/src/pages/Dashboard.tsx` (T019/T025/T030), `web_admin/src/services/api.ts` (T017/T024/T029/T034), `backend/app/application/evaluation_use_case.py` (T014/T015/T027/T032), and `backend/app/api/v1/router_evaluations.py` (T016/T023/T028/T033). Different stories editing these must run sequentially.

---

## Parallel Example: Foundational Phase

```bash
Task: "T004 Domain dataclasses in backend/app/domain/models.py"
Task: "T006 ORM models in backend/app/adapters/persistence/orm_models.py"
Task: "T007 Ports in backend/app/domain/ports/{learning_outcome,evaluation}_repository.py"
Task: "T010 Pydantic schemas in backend/app/api/schemas/evaluation_schemas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 Setup → 2. Phase 2 Foundational (CRITICAL) → 3. Phase 3 US1.
4. **STOP and VALIDATE**: a mentor evaluates a student for a week with pre-fill, and it persists.
5. Deploy/demo — this alone delivers the core weekly-evaluation capability.

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. US1 → test → deploy (MVP: capture + pre-fill).
3. US2 → test → deploy (catalog management).
4. US3 → test → deploy (dashboard).
5. US4 → test → deploy (weekly export).

### Parallel Team Strategy

After Foundational, Developer A takes US1, B takes US2 (catalog), C takes US3 (dashboard), D takes
US4 (export); serialize the shared files listed above. Stories integrate independently.

---

## Notes

- [P] = different files, no incomplete-task dependency.
- [Story] label maps each task to its user story for traceability.
- Verify every test fails before implementing (constitution Principle V).
- Mentor = `tipo == STAFF` OR `role` in ADMIN/SUPER_ADMIN, scoped to their single `turma_ou_equipe`; catalog writes admin-only; evaluation data staff-only (no ALUNO access).
- Co-evaluation: one evaluation per student/week; levels upsert last-write-wins with mentor attribution; each mentor's comment kept separately.
- Week is an integer derived from `config` keys `lo_eval_data_inicio` / `lo_eval_num_semanas`; no new dependencies in this feature.
- Commit after each task or logical group; stop at any checkpoint to validate a story independently.
