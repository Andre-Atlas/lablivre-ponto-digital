# Phase 0 Research: Medical Certificates & Absence Justification

All Technical Context unknowns are resolved below. Each entry records the decision, why it
was chosen, and the alternatives weighed. Decisions are constrained by the project
constitution (Stack Stability, Async & Stateless, Security & RBAC).

## R1 — How to represent "an absent day linked to a certificate"

**Decision**: Model justification as an explicit `certificate_days` link table enumerating
each `(student, date, turno)` a certificate covers, and have the attendance computation
treat a shift as `JUSTIFICADO` when an **active** certificate-day link exists for it (and no
real present/late check-in does). Do **not** create dummy `JUSTIFICADO` check-ins for
certificates.

**Link-eligibility rule** (clarified 2026-10-09): on save, a `certificate_days` row is
created for every expected shift in `[periodo_inicio, periodo_fim]` that **lacks a real
present/late check-in** — i.e. the shift is currently a FALTA *or* was already JUSTIFICADO
(e.g. by the legacy manual flow). This records the document-backed origin even when a prior
manual justification existed. Shifts with a real present/late check-in are never linked.
Certificates apply to `ALUNO` students only.

**Rationale**:
- Absences are computed, not stored (`router_admin.py` export derives `FALTA` from the
  absence of a `Checkin` for an expected `turno_referencia`). A link table lets a certificate
  justify both already-elapsed absences and future days in range uniformly (FR-006, FR-009).
- An explicit link satisfies the user's core requirement — the certificate "keeps linked to
  the day the student is absent" — and makes both-direction traceability (FR-010, FR-011) and
  overlap handling (FR-016) trivial queries.
- Revocation (FR-013) is a status flip; the days it solely justified revert automatically
  because the computation stops seeing an active link — no attendance rows to clean up.

**Alternatives considered**:
- *Reuse the existing dummy-`JUSTIFICADO`-checkin mechanism*: rejected — pollutes `checkins`
  with synthetic rows on a fake `JUSTIFICADO_WEB` device, cannot represent overlap or clean
  revocation, and conflicts with the unique `(user_id, turno_referencia)` constraint when a
  real late check-in later arrives.
- *Store the covered range only (no per-day rows) and expand at query time*: rejected as the
  primary store — expansion still needs the turma's expected-shift grid; a materialized
  per-day link is simpler to join in the export and to display. (The range is still stored on
  the certificate for audit/UI; the per-day rows are derived from it at record time and when
  coverage is re-resolved.)

## R2 — Where to store the certificate document (stateless constraint)

**Decision**: Store the document bytes in PostgreSQL as a `LargeBinary` (BYTEA) column on
`medical_certificates`, with `content_type` and `filename` metadata. Serve downloads through
an admin-only endpoint that streams the bytes.

**Rationale**:
- Constitution Principle III forbids pod-local disk state; the managed Postgres is the single
  source of truth, so bytes-in-DB keeps pods disposable with zero new infrastructure.
- No object-storage client exists in the stack (no boto3/supabase/aiofiles); Principle I says
  reuse before adding. BYTEA needs no new dependency.
- Scale is tiny (hundreds of students, a few MB per certificate, few per term), so DB size and
  row-read cost are non-issues. A 10 MB application-level cap bounds worst case.

**Alternatives considered**:
- *Supabase Storage / S3 bucket*: rejected for v1 — introduces a new integration, credentials,
  and failure mode for no benefit at this scale; revisit only if document volume grows.
- *Local/pod filesystem*: rejected — violates Principle III (state lost on pod recycle).

## R3 — How to receive the uploaded file in FastAPI

**Decision**: Accept the certificate via `multipart/form-data` using FastAPI `UploadFile` +
`Form` fields (student id, start date, end date, optional note). Add `python-multipart` to
`backend/requirements.txt`.

**Rationale**: `UploadFile` streams the file without loading it wholly into memory up front
and is the idiomatic FastAPI pattern for binary uploads alongside form fields. `python-multipart`
is required by Starlette/FastAPI to parse multipart bodies; it is small, maintained, and stays
within the backend layer (permitted additive dependency under Principle I, logged in the plan's
Complexity Tracking).

**Alternatives considered**:
- *Base64 document inside a JSON body*: rejected — avoids the dep but inflates payload ~33%,
  is awkward at 10 MB, and is non-idiomatic for file upload.

**Validation**: enforce allowed content types (`application/pdf`, `image/jpeg`, `image/png`)
and a max size (10 MB) before persisting; reject others with a clear 4xx (FR-017, FR-003).

## R4 — Mapping a covered date range to justifiable shifts

**Decision**: Reuse the existing expected-shift grid (`TURNOS_ALUNOS`, `_DIA_SEMANA_MAP` in
`app/domain/models.py`). For a certificate covering `[start, end]`, the domain computes every
`(date, turno)` in range that is an expected shift for the student's `turma_ou_equipe`; those
become `certificate_days` rows. Days with no expected shift (weekends, non-class days) are
skipped (edge case: certificate covering only non-working days links to zero days).

**Rationale**: Keeps a single source of truth for "which shifts a student owes" and guarantees
the certificate justifies exactly the days the export would otherwise count as `FALTA`
(FR-006, FR-007). Keeping this in the domain layer (framework-free) satisfies Principle II and
is directly unit-testable (Principle V).

**Alternatives considered**:
- *Justify calendar days regardless of the turma grid*: rejected — would mark non-class days
  as justified and diverge from how the export computes faltas.

## R5 — Keeping the export consistent with certificate coverage

**Decision**: In **both** export branches (CSV and Excel), when a shift has no present/late
check-in, consult active certificate coverage for that `(student, date, turno)`; if covered,
emit `JUSTIFICADO` and attribute the certificate (identifier) in the output column instead of
`FALTA`. Batch-load the student's active certificate-days for the export window to avoid
per-shift queries.

**CSV rework** (clarified 2026-10-09): the CSV branch today is a raw check-in dump and does
not compute faltas at all. To satisfy the clarified FR-012 ("both CSV and Excel reflect
certificate justification"), the CSV branch is reworked to enumerate expected shifts per
`ALUNO` (mirroring the Excel falta logic) and report `FALTA`/`JUSTIFICADO`, with certificate
attribution. The expected-shift enumeration is shared between branches to avoid divergence.

**Rationale**: Satisfies FR-012 across both reports while reusing one expected-shift
computation. Batching preserves the current performance budget.

**Alternatives considered**:
- *Reflect certificates only in the Excel report, leave CSV as a raw dump*: rejected per the
  2026-10-09 clarification (user requires both exports to reflect certificate justification).
- *Precompute/materialize JUSTIFICADO checkins so the export needs no change*: rejected per R1
  (pollutes attendance, breaks on later real check-ins).

## R6 — Database migration strategy

**Decision**: Add an Alembic migration under `backend/alembic/versions/` creating
`medical_certificates` and `certificate_days` with their indexes and FKs. If no baseline
revision exists yet (the `versions/` directory is currently empty), the migration author must
first generate/confirm a baseline for the existing schema so the new revision has a valid
`down_revision`, OR explicitly set `down_revision = None` for a greenfield-from-here chain —
decided during implementation against the actual deployed DB state.

**Rationale**: Alembic is already configured (`alembic.ini`); using it keeps schema changes
versioned and reviewable (constitution governance). The empty `versions/` directory is a
pre-existing gap flagged here as a risk to resolve at implementation time, not a new design
decision for this feature.

**Alternatives considered**:
- *`Base.metadata.create_all()` at startup*: rejected — not migration-safe for production and
  inconsistent with the Alembic setup already present.

## R7 — Overlap and revocation semantics

**Decision**: A `(student, date, turno)` may have more than one active certificate-day link.
A shift is justified while **≥1** linked certificate is `ACTIVE`. Revoking a certificate sets
its status to `REVOKED` and deactivates its links; the shift reverts to `FALTA` only if no
other active certificate still covers it (FR-016). Certificate records and their audit
timestamps are retained after revocation (FR-013, FR-014).

**Rationale**: Directly encodes the spec's overlap and revocation edge cases with simple
status-based filtering; no destructive deletes, preserving the audit trail.

## Resolved unknowns summary

| Unknown | Resolution |
|---------|------------|
| Day↔certificate linkage model | Explicit `certificate_days` link table; export consults active links (R1) |
| Document storage under stateless rule | Postgres BYTEA, admin-only streaming download (R2) |
| File upload mechanism / new dep | `multipart/form-data` + `UploadFile`; add `python-multipart` (R3) |
| Range → justifiable shifts | Reuse `TURNOS_ALUNOS`/`_DIA_SEMANA_MAP` grid in the domain (R4) |
| Export consistency | Batch-load active coverage; emit JUSTIFICADO + certificate id (R5) |
| Migrations | Alembic revision for 2 tables; resolve baseline gap at impl time (R6) |
| Overlap / revoke | Multi-link allowed; justified while ≥1 ACTIVE; revoke = status flip (R7) |

No `NEEDS CLARIFICATION` items remain.
