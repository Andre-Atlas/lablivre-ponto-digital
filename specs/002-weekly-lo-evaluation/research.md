# Phase 0 Research: Weekly Learning-Outcome Evaluation

All Technical Context unknowns are resolved below (decision / rationale / alternatives),
constrained by the project constitution (Stack Stability, Async & Stateless, Security & RBAC).

## R1 — Evaluation data model (student × week × LO, with co-evaluation)

**Decision**: One `WeeklyEvaluation` row per `(student, week)`. Per-LO levels live in a child
`lo_evaluation_levels` table — one row per `(evaluation, learning_outcome)` with the level (1–4)
and the `mentor_id` who last set it; unique on `(evaluation_id, lo_id)`. Comments live in a child
`lo_evaluation_comments` table — one row per `(evaluation, mentor)`, unique on `(evaluation_id,
mentor_id)`. A re-save **upserts**: each submitted LO level updates its row (last-write-wins,
`updated_at`/`mentor_id` refreshed), and the submitting mentor's comment replaces only their own
comment row. Both mentors' comments therefore coexist (clarification 2026-10-13).

**Rationale**: Directly encodes "one evaluation per student/week", partial evaluation (only some
LOs set), last-write-wins per LO with attribution, and multi-mentor comments — all read back
cheaply with indexed joins. No synthetic rows; history is intrinsic.

**Alternatives considered**:
- *One flat row per (student, week, LO)* with no parent: rejected — makes "assessed vs pending"
  and per-week comment handling awkward and scatters the week concept.
- *A separate independent evaluation per mentor*: rejected per clarification (adds reconciliation
  complexity on dashboard/report for no stated need).

## R2 — Defining a "week"

**Decision**: A week is an integer index ≥ 1 derived from a configured program **start date**
(`data_inicio_semana1`) and a configured **number of weeks** (`num_semanas`, default 12), stored
in the existing `config` key-value table (keys `lo_eval_data_inicio`, `lo_eval_num_semanas`).
`semana_de(data, inicio) = floor((data - inicio).days / 7) + 1`. Evaluations for weeks `< 1` or
`> num_semanas` are rejected (FR-013). The current week is `semana_de(today, inicio)` clamped to
the range.

**Rationale**: Matches the reference program (`dataInicioSemana1`, `maxWeeks`) and reuses the
`Config` table rather than adding a new settings table (Principle I — reuse before add). Keeping
the derivation a pure domain function makes it unit-testable (Principle II/V).

**Alternatives considered**:
- *A dedicated `program_config` table*: rejected for v1 — the key-value `config` table already
  serves this purpose; revisit only if settings grow structured.
- *User picks an arbitrary calendar date range per evaluation*: rejected — the program is weekly
  by design; an integer week keeps dashboards/reports and pre-fill well-defined.

## R3 — Pre-fill with last known levels

**Decision**: For a student and target week `W`, pre-fill each active LO with the level from the
**most recent prior** evaluation (`week < W`) that has a level for that LO; blank if none. Computed
by selecting, per `lo_id`, the level from the highest `week < W` with a row for that student+LO.

**Rationale**: Satisfies FR-003 exactly and mirrors the reference `latestLevelsBefore`. Indexed by
`(student, week)` and `(evaluation, lo)`, it is a bounded per-request query.

## R4 — Dashboard aggregates (assessed/pending, byMentor, heatmap, regressions)

**Decision**: Compute server-side for a `(turma, week)`:
- **assessed/pending**: turma = ALUNO users with `turma_ou_equipe == turma`; assessed = those with
  a `WeeklyEvaluation` for the week; pending = the rest (with identities).
- **byMentor**: count of distinct students each mentor touched that week (distinct `mentor_id` over
  the week's `lo_evaluation_levels`, plus comment authors).
- **heatmap**: per active LO, the distribution of levels (counts of 1/2/3/4) across the turma for
  the week.
- **regressions**: for each student+LO assessed in week `W`, compare to that student's most recent
  comparable prior-week level for the same LO (via R3's query with `week < W`); flag when strictly
  lower. Only flagged when a comparable prior level exists (handles partial prior weeks).

**Rationale**: Encodes FR-009/010/011 and the reference `dashboardModel`. All aggregates come from
batched, indexed queries over the week's rows; turma size is small so this stays well within the
performance budget.

**Alternatives considered**:
- *Precomputed/materialized dashboard rows*: rejected — unnecessary at this scale and adds write
  complexity; compute-on-read is simpler and always correct.

## R5 — Weekly report export

**Decision**: Add a report endpoint that returns a `StreamingResponse` (CSV or Excel via openpyxl)
listing, for a `(turma, week)`, each student with a column per active LO (their level or blank) and
the week's comments; students without an evaluation are rowed as **pending**. Reuses the existing
export patterns in `router_admin.py` (openpyxl workbook / `csv.writer`), no new dependency.

**Rationale**: Satisfies FR-012 while staying consistent with the platform's current export engine
and format conventions.

**Alternatives considered**:
- *Extend the existing `/admin/export/checkins` endpoint*: rejected — different domain and columns;
  a dedicated evaluations export endpoint is clearer and keeps attendance export untouched.
- *PDF / AI summary*: out of scope (would add dependencies; excluded by spec).

## R6 — Roles, turma scoping, and visibility

**Decision**: Add a `require_mentor` dependency allowing any **STAFF** user (`tipo == STAFF`) or any
**ADMIN/SUPER_ADMIN** (by `role`). Recording an evaluation additionally requires the mentor's
`turma_ou_equipe` to equal the student's (FR-006). LO **catalog CRUD** stays behind the existing
`require_admin` (ADMIN/SUPER_ADMIN only, FR-008). Dashboard and report require `require_mentor`.
Students (ALUNO) have no access to any evaluation endpoint (FR-014).

**Rationale**: Mentors are STAFF/ADMIN per the spec; the existing `require_admin` is too narrow for
the mentor role (excludes STAFF), so a sibling dependency is the minimal correct addition. Turma
scoping is a server-side check, never UI-only (Principle IV).

## R7 — Database migration

**Decision**: One Alembic revision chained to the current head `a02dab1dca18`, creating
`learning_outcomes`, `lo_evaluations`, `lo_evaluation_levels`, `lo_evaluation_comments` with their
FKs, indexes, and unique constraints. (The medical-certificate migration lives on a separate
feature branch and is intentionally absent here; the two will reconcile at merge.)

**Rationale**: Alembic is already wired in `backend/migrations/`; a single additive revision keeps
schema changes versioned and reviewable (constitution governance).

## Resolved unknowns summary

| Unknown | Resolution |
|---------|------------|
| Evaluation storage + co-evaluation | Parent per (student,week) + per-LO level rows (upsert, last-write-wins, mentor-attributed) + per-mentor comments (R1) |
| "Week" definition | Integer index from configured start date + num weeks in `config` table (R2) |
| Pre-fill | Most recent prior-week level per LO per student (R3) |
| Dashboard aggregates | Compute-on-read: assessed/pending, byMentor, heatmap, regressions (R4) |
| Report export | Dedicated endpoint, openpyxl/CSV, pending marker; reuse existing patterns (R5) |
| Roles / scoping / visibility | `require_mentor` (STAFF/ADMIN) + turma match; catalog admin-only; staff-only (R6) |
| Migration | One Alembic revision chained to `a02dab1dca18` (R7) |

No `NEEDS CLARIFICATION` items remain.
