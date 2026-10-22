# Implementation Plan: Weekly Learning-Outcome Evaluation

**Branch**: `002-weekly-lo-evaluation` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-weekly-lo-evaluation/spec.md`

## Summary

Mentors (STAFF/ADMIN, scoped to their own `turma_ou_equipe`) evaluate each student (ALUNO)
once per program **week**, assigning a level **1–4** to one or more **learning outcomes (LOs)**
plus per-mentor comments; the form pre-fills each LO with the student's most recent prior level.
Admins manage the **LO catalog**. A per-turma/week **dashboard** shows assessed-vs-pending,
per-mentor counts, a level **heatmap** per LO, and **regressions** vs the prior week. A **weekly
report** exports per-student levels + comments via the platform's existing openpyxl/CSV engine.

**Technical approach**: Purely additive, following the existing hexagonal layout and reusing the
`User` model (ALUNO = student; STAFF/ADMIN = mentor) and the `Config` key-value table for program
settings (start date, number of weeks) — **no new dependencies** (openpyxl already present; no
file upload). A **week** is an integer index derived from the configured start date. Evaluations
are stored as one `WeeklyEvaluation` per `(student, week)` with a child `EvaluationLevel` per LO
(unique per `(evaluation, LO)`, last-write-wins on re-save, carrying the mentor who set it) and a
child `EvaluationComment` per `(evaluation, mentor)` (both mentors' comments kept). Dashboard and
report are read-side computations over these tables. Delivered test-first.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 6 / React 19 (frontend) — unchanged per
constitution Principle I (Stack Stability).

**Primary Dependencies**: FastAPI, async SQLAlchemy 2.x over asyncpg, Pydantic v2, Alembic,
python-jose (JWT); React 19 + Vite + Tailwind CSS 4 + Lucide, raw `fetch` + Bearer token in
localStorage (matching `web_admin/src/services/api.ts`). Reporting reuses **openpyxl** (already a
dependency). **No new dependencies are introduced.**

**Storage**: PostgreSQL (managed), accessed 100% async. New tables: `learning_outcomes`,
`lo_evaluations`, `lo_evaluation_levels`, `lo_evaluation_comments`. Program settings stored in the
existing `config` key-value table. Alembic migration required (chains to current head
`a02dab1dca18`).

**Testing**: pytest + pytest-asyncio (backend; suite runs on `sqlite+aiosqlite` locally, Postgres
in CI); Playwright (frontend E2E, existing dev dependency).

**Target Platform**: Linux containers on Kubernetes (prod) / docker-compose (dev); stateless SPA
frontend. Stateless compute per constitution Principle III.

**Project Type**: Decoupled web application — `backend/` (FastAPI) + `web_admin/` (React),
communicating only over `/api/v1/*` with JWT (Principle II).

**Performance Goals**: Interactive staff actions — p95 < 500 ms for submitting an evaluation and
for loading a turma's weekly dashboard (dashboard aggregates are computed from indexed queries
batched per request; turma size is low hundreds).

**Constraints**: Evaluation data is staff-only (mentors/admins; not students) per FR-014; mentors
restricted to their own turma per FR-006; LO catalog management admin-only; all DB access async;
contract defined before implementation; no stack change.

**Scale/Scope**: University-lab scale — low hundreds of students, ~2 turmas, ~12 weeks, a few
dozen LOs. ~4 new backend tables, 2 ports + repos, 2 use cases, 1 new router (catalog CRUD +
evaluation submit + prefill + dashboard + export), and admin-panel UI (evaluation form, dashboard,
catalog manager).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Stack Stability | ✅ PASS | Reuses the existing stack with **zero new dependencies**; no new language/framework/DB engine/service. |
| II. Contract-First & Decoupled Services | ✅ PASS | API contract authored in Phase 1 before implementation; exposed only via `/api/v1/*`; week-derivation, pre-fill, dashboard and regression logic live in the framework-free domain/application layers. |
| III. Async & Stateless by Default | ✅ PASS | All new DB access async; no server-side session or disk state; JWT auth unchanged. |
| IV. Security & RBAC by Design | ✅ PASS | New `require_mentor` (STAFF/ADMIN) for evaluations/dashboard/report; catalog CRUD behind `require_admin`; turma scoping enforced server-side; students cannot access evaluation data; Pydantic validation at the boundary. |
| V. Test-First Quality Gates | ✅ PASS | TDD: domain unit tests (week derivation, pre-fill, regression) + integration tests (submit/catalog/dashboard/export + RBAC) written first; target ≥80% backend coverage; Playwright E2E for the evaluation flow. |
| VI. Impeccable UX & Living Documentation | ✅ PASS | New admin-panel UI ships loading/empty/error states, Light/Dark, a11y; OpenAPI auto-updates; README/ARCHITECTURE/CHANGELOG updated in the same change. |

**Initial gate: PASS.** Post-Phase-1 re-evaluation: **PASS** (design keeps domain logic
framework-free and stores all state in the managed DB; no new deps).

## Project Structure

### Documentation (this feature)

```text
specs/002-weekly-lo-evaluation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── weekly-lo-evaluation.openapi.yaml
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

New/modified files follow the existing hexagonal structure. No new top-level projects.

```text
backend/
├── app/
│   ├── domain/
│   │   ├── models.py                          # + LearningOutcome, WeeklyEvaluation,
│   │   │                                       #   EvaluationLevel, EvaluationComment dataclasses;
│   │   │                                       #   semana_de(data,inicio), prefill & regression helpers
│   │   └── ports/
│   │       ├── learning_outcome_repository.py  # NEW port
│   │       └── evaluation_repository.py        # NEW port
│   ├── application/
│   │   ├── lo_catalog_use_case.py              # NEW: catalog CRUD
│   │   └── evaluation_use_case.py              # NEW: submit, prefill, dashboard, report-data
│   ├── adapters/
│   │   └── persistence/
│   │       ├── orm_models.py                   # + 4 ORM tables
│   │       ├── learning_outcome_repo_impl.py   # NEW
│   │       └── evaluation_repo_impl.py         # NEW
│   └── api/
│       ├── middleware/auth_dependencies.py     # + require_mentor (STAFF/ADMIN)
│       ├── schemas/evaluation_schemas.py       # NEW Pydantic models
│       └── v1/
│           └── router_evaluations.py           # NEW router (/admin/avaliacoes + /admin/los) + main.py
├── migrations/versions/<rev>_weekly_lo_evaluation.py  # NEW (chains to a02dab1dca18)
└── tests/
    ├── unit/test_evaluation_domain.py          # week derivation, prefill, regression, validation
    └── integration/
        ├── test_lo_catalog_api.py              # catalog CRUD + RBAC
        ├── test_evaluation_api.py              # submit/prefill + turma scoping + co-eval + RBAC
        ├── test_dashboard_api.py               # assessed/pending, byMentor, heatmap, regressions
        └── test_evaluation_export.py           # weekly report CSV/Excel

web_admin/
└── src/
    ├── services/api.ts                         # + catalog, evaluation, prefill, dashboard, export calls
    ├── pages/Dashboard.tsx                      # + entry points for the three panels
    └── components/
        ├── AvaliacoesPanel.tsx                  # weekly evaluation form (per student/week)
        ├── LODashboardPanel.tsx                 # dashboard (counts, heatmap, regressions)
        └── LOCatalogPanel.tsx                   # admin LO catalog manager
    └── (Playwright E2E under web_admin/tests/e2e/)
```

**Structure Decision**: Decoupled web-app structure (Principle II). All backend work slots into
the existing `domain → application → adapters → api` hexagon; all frontend work extends the
existing `web_admin/src` SPA and its `services/api.ts` client. No new service or deployment unit.

## Complexity Tracking

> No constitution violations. This feature introduces **no new dependencies** and no new
> architectural patterns — it reuses the hexagonal layout, the `User` model, the `Config`
> key-value table, and the openpyxl export already in the stack. Nothing to justify here.
