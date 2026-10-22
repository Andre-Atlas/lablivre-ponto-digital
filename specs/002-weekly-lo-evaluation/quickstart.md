# Quickstart & Validation: Weekly Learning-Outcome Evaluation

This guide proves the feature end-to-end. It references [data-model.md](./data-model.md) and
[contracts/weekly-lo-evaluation.openapi.yaml](./contracts/weekly-lo-evaluation.openapi.yaml); it
does not duplicate schema or include implementation code.

## Prerequisites

- Stack running via docker-compose (see root `README.md`): backend `http://localhost:8000`
  (Swagger `/docs`), frontend `http://localhost:5173`.
- Apply the new Alembic migration: `cd backend && alembic upgrade head`.
- Seed the program config in the `config` table (or via an admin tool): `lo_eval_data_inicio`
  (an ISO date defining week 1) and `lo_eval_num_semanas` (e.g., 12).
- An **admin** (ADMIN/SUPER_ADMIN) and a **mentor** that is STAFF in `Turma 1`; at least two
  **students** (ALUNO) in `Turma 1`. Obtain JWTs via the existing login; export
  `ADMIN_TOKEN`, `MENTOR_TOKEN`.

## Backend checks (from `backend/`)

```bash
pytest tests/unit/test_evaluation_domain.py \
       tests/integration/test_lo_catalog_api.py \
       tests/integration/test_evaluation_api.py \
       tests/integration/test_dashboard_api.py \
       tests/integration/test_evaluation_export.py -v

pytest --cov=app --cov-report=term-missing   # Principle V: >= 80% on new modules
```

## Scenario 1 — Admin manages the LO catalog (US2)

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/los \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"numero":1,"nome":"Pensamento computacional","descricao":"..."}'
curl -s http://localhost:8000/api/v1/admin/los -H "Authorization: Bearer $MENTOR_TOKEN"
```

**Expected**: 201 for the create; the list shows the active outcome. A non-admin creating → 403.
Deactivating an outcome (`PUT .../los/{id}` with `{"ativo":false}`) removes it from new lists while
past evaluations keep it.

## Scenario 2 — Mentor records a weekly evaluation, with pre-fill (US1)

```bash
# Pre-fill for week 3 (blank for a never-assessed student)
curl -s "http://localhost:8000/api/v1/admin/avaliacoes/prefill?user_id=<ALUNO>&semana=3" \
  -H "Authorization: Bearer $MENTOR_TOKEN"

# Submit week 3 for two LOs + a comment
curl -s -X POST http://localhost:8000/api/v1/admin/avaliacoes \
  -H "Authorization: Bearer $MENTOR_TOKEN" -H "Content-Type: application/json" \
  -d '{"user_id":"<ALUNO>","semana":3,"niveis":{"<LO1>":2,"<LO2>":3},"comentario":"Boa evolução"}'

# Week 4 pre-fill now reflects week 3
curl -s "http://localhost:8000/api/v1/admin/avaliacoes/prefill?user_id=<ALUNO>&semana=4" \
  -H "Authorization: Bearer $MENTOR_TOKEN"
```

**Expected**: submit returns 200 with the saved levels (attributed to the mentor) and comment;
week-4 pre-fill returns `{<LO1>:2,<LO2>:3}`. Negative checks: a level of 5 or an inactive LO → 400;
a mentor from another turma → 403; a week outside the program range → 400.

## Scenario 3 — Co-evaluation (clarified behavior)

A second mentor (same turma) submits week 3 for `<ALUNO>` changing `<LO1>` to 4 with their own
comment. `GET /admin/avaliacoes?user_id=<ALUNO>&semana=3` shows `<LO1>=4` (last write wins) and
**both** mentors' comments.

## Scenario 4 — Dashboard (US3)

```bash
curl -s "http://localhost:8000/api/v1/admin/avaliacoes/dashboard?turma=Turma%201&semana=3" \
  -H "Authorization: Bearer $MENTOR_TOKEN"
```

**Expected**: `avaliados`/`pendentes` correctly split the turma; `por_mentor` tallies each mentor's
assessed students; `heatmap` shows level counts per LO; `regressoes` lists any student+LO whose
week-3 level is below their most recent prior week.

## Scenario 5 — Weekly report export (US4)

```bash
curl -s "http://localhost:8000/api/v1/admin/avaliacoes/export?turma=Turma%201&semana=3&format=csv" \
  -H "Authorization: Bearer $MENTOR_TOKEN" -o relatorio_semana3.csv
```

**Expected**: one row per Turma 1 student — a column per active LO with the level or blank, plus the
week's comments; un-evaluated students are marked pending.

## Scenario 6 — RBAC & visibility (FR-008/FR-014)

```bash
# Student token must be rejected everywhere
curl -s -o /dev/null -w "%{http_code}\n" \
  "http://localhost:8000/api/v1/admin/avaliacoes/dashboard?turma=Turma%201&semana=3" \
  -H "Authorization: Bearer $ALUNO_TOKEN"   # expect 403
# Catalog write requires admin
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/api/v1/admin/los \
  -H "Authorization: Bearer $MENTOR_TOKEN" -H "Content-Type: application/json" -d '{"numero":9,"nome":"x"}'
# expect 403 if the mentor is STAFF (non-admin)
```

## Frontend check (Dashboard, Playwright E2E)

1. Log in as a mentor; open **Avaliações LOs**.
2. Pick a student and week; the form pre-fills prior levels; set levels + comment; save.
3. Confirm loading/empty/error states, Light/Dark, keyboard accessibility.
4. Open the **Dashboard** tab: assessed/pending, per-mentor, heatmap, regressions render.
5. As an admin, open **Catálogo de LOs** and add/deactivate an outcome.

## Done when

- All backend tests pass with ≥ 80% coverage on new modules.
- Scenarios 1–6 behave as described against a running stack.
- The Playwright E2E for the evaluation flow passes.
- OpenAPI (`/docs`), README, ARCHITECTURE, and CHANGELOG updated (Principle VI).
