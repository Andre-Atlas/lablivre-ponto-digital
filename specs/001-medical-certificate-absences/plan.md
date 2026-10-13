# Implementation Plan: Medical Certificates & Absence Justification

**Branch**: `001-medical-certificate-absences` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-medical-certificate-absences/spec.md`

## Summary

Administrators record a medical certificate (document + contiguous covered period) for a
student of type **ALUNO**; on save, every expected working-shift within that period for which
the student has **no real present/late check-in** (a FALTA, or an already-JUSTIFICADO shift)
is marked **justified** and permanently **linked** to the certificate, including shifts whose
absence is only determined later. The link is traceable both ways (day → certificate+document,
certificate → days) and is reflected in **both** attendance exports (CSV and Excel). Admins
can revoke a certificate, reverting the shifts it solely justified.

**Technical approach**: Absences are not stored today — a `FALTA` is the *absence* of a
`Checkin` for an expected `turno_referencia` (`"{YYYY-MM-DD}_{MANHA|TARDE}"`), and the
attendance export computes it on the fly (Excel branch only today; the CSV branch is a raw
check-in dump). Rather than fabricate dummy `JUSTIFICADO` check-ins (the current manual
`justificar` approach), this feature introduces a certificate aggregate plus an explicit
**certificate-day link** table enumerating each `(student, date, turno)` a certificate
justifies — materialized for every expected shift in range lacking a real present/late
check-in. Both export branches consult active certificate-day links so coverage applies
uniformly to past and future absences without polluting the `checkins` table; per clarification
the **CSV branch is reworked** to enumerate expected shifts (FALTA/JUSTIFICADO) like the Excel
report. Documents are stored as bytes in PostgreSQL (no pod-disk state, no new storage
integration) and served only to admins. All new code follows the existing hexagonal layout
(domain model + port → application use case → persistence adapter → versioned API router) and
is delivered test-first.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 6 / React 19 (frontend) — unchanged
per constitution Principle I (Stack Stability).

**Primary Dependencies**: FastAPI, async SQLAlchemy 2.x over asyncpg, Pydantic v2, Alembic,
python-jose (JWT), bcrypt/passlib; React 19 + Vite + Tailwind CSS 4 + Lucide, raw `fetch`
with Bearer token in localStorage (matching existing `web_admin/src/services/api.ts`).
**One additive backend dependency**: `python-multipart` (required by FastAPI to accept the
uploaded document via `multipart/form-data`). Justified under Principle I as a minor,
in-layer, actively-maintained addition that introduces no new architecture.

**Storage**: PostgreSQL (managed — Supabase/Neon), accessed 100% async. Certificate document
bytes stored in a `LargeBinary` column (BYTEA), max **10 MB** per document. New tables:
`medical_certificates`, `certificate_days`. Alembic migration required.

**Testing**: pytest + pytest-asyncio (backend, existing suite runs on `sqlite+aiosqlite`);
Playwright (frontend E2E, already a dev dependency).

**Target Platform**: Linux containers on Kubernetes (prod) / docker-compose (dev); frontend
served as a static SPA. Stateless compute per constitution Principle III.

**Project Type**: Decoupled web application — `backend/` (FastAPI) + `web_admin/` (React),
communicating only over `/api/v1/*` with JWT (constitution Principle II).

**Performance Goals**: Interactive admin actions — p95 < 500 ms for recording/revoking a
certificate (excluding document transfer); document upload accepts files up to ~10 MB.
Attendance export remains within its current time budget despite the added certificate
lookup (lookups are indexed and batched per request).

**Constraints**: Certificates apply to `ALUNO` students only (STAFF out of scope — no falta
computation to justify); no pod-local persistence (documents live in the managed DB); document
retrieval is admin-only (sensitive health data); all DB access async and non-blocking;
contract defined before implementation; no change to the locked stack beyond the single
justified additive dependency.

**Scale/Scope**: University-lab scale — low hundreds of students, a handful of certificates
per student per term, documents a few MB each. ~2 new backend tables, ~1 port + repo, ~1
use case, ~1 router (4–5 endpoints), and an admin-panel UI section in the existing Dashboard.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Stack Stability | ✅ PASS | Reuses existing stack. One minor additive, in-layer dep (`python-multipart`) justified in Complexity Tracking; no new language/framework/DB engine/storage service. |
| II. Contract-First & Decoupled Services | ✅ PASS | API contract authored in Phase 1 (`contracts/`) before implementation; feature exposed only via `/api/v1/admin/*`; domain logic (coverage computation) isolated from FastAPI and SQLAlchemy. |
| III. Async & Stateless by Default | ✅ PASS | All new DB access async; document bytes in managed Postgres (no disk/session state); JWT auth unchanged. |
| IV. Security & RBAC by Design | ✅ PASS | All endpoints behind `require_admin` (SUPER_ADMIN/ADMIN); document download admin-only; inputs validated by Pydantic; file type/size validated; no secrets added. |
| V. Test-First Quality Gates | ✅ PASS | TDD: domain coverage-computation unit tests + repo/endpoint integration tests written before implementation; target ≥80% backend coverage; Playwright E2E for the admin flow. |
| VI. Impeccable UX & Living Documentation | ✅ PASS | New Dashboard section ships loading/empty/error states, Light/Dark, a11y; OpenAPI auto-updates; README/ARCHITECTURE/CHANGELOG updated in the same change. |

**Initial gate: PASS.** Re-evaluation after Phase 1 design: **PASS** (no new violations; the
design keeps domain logic framework-free and stores state only in the managed DB).

## Project Structure

### Documentation (this feature)

```text
specs/001-medical-certificate-absences/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI fragment for the new endpoints)
│   └── medical-certificates.openapi.yaml
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

New and modified files follow the existing hexagonal structure. No new top-level projects.

```text
backend/
├── app/
│   ├── domain/
│   │   ├── models.py                         # + MedicalCertificate, CertificateDay dataclasses
│   │   ├── enums.py                          # + CertificateStatus (ACTIVE, REVOKED)
│   │   ├── services (in models.py)           # + coverage computation: expected shifts in a date range
│   │   └── ports/
│   │       └── certificate_repository.py     # NEW port (ABC)
│   ├── application/
│   │   └── certificate_use_case.py           # NEW: record / revoke / get / list / resolve-coverage
│   ├── adapters/
│   │   └── persistence/
│   │       ├── orm_models.py                 # + MedicalCertificateModel, CertificateDayModel
│   │       └── certificate_repo_impl.py      # NEW repo adapter
│   └── api/
│       ├── schemas/
│       │   └── certificate_schemas.py        # NEW Pydantic request/response models
│       └── v1/
│           ├── router_certificates.py        # NEW router (/admin/certificados) + include in main.py
│           └── router_admin.py               # MODIFIED: BOTH export branches (CSV + Excel) consult certificate coverage for JUSTIFICADO; CSV reworked to enumerate expected shifts
├── alembic/
│   └── versions/
│       └── <rev>_medical_certificates.py     # NEW migration (create 2 tables; baseline if needed)
└── tests/
    ├── unit/
    │   └── test_certificate_domain.py        # coverage computation, validation
    └── integration/
        ├── test_certificate_api.py           # record/revoke/get/list + RBAC + document download
        └── test_export_with_certificates.py  # CSV and Excel exports show JUSTIFICADO for covered absences

web_admin/
└── src/
    ├── services/
    │   └── api.ts                            # + certificate API calls (record multipart, list, revoke, download)
    ├── pages/
    │   └── Dashboard.tsx                     # + "Atestados" section/modal (upload, list, revoke, view doc)
    └── (tests via Playwright)                # E2E: admin records a certificate, days show justified
```

**Structure Decision**: Decoupled web-app structure (constitution Principle II). All backend
work slots into the existing `domain → application → adapters → api` hexagon; all frontend
work extends the existing `web_admin/src` SPA and its `services/api.ts` client. No new
service, project, or deployment unit is introduced.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Add `python-multipart` dependency | FastAPI requires it to parse `multipart/form-data` for the document upload; it is the idiomatic way to receive a binary file alongside form fields. | Base64-encoding the document inside a JSON body avoids the dep but inflates payloads ~33%, complicates 10 MB uploads, and is non-idiomatic. The dep is tiny, in-layer, and maintained — permitted additive change under Principle I. |
| New `certificate_days` link table (vs. reusing dummy `JUSTIFICADO` check-ins) | Gives an explicit, queryable day↔certificate link (FR-008/010/011), clean overlap handling (FR-016), and correct future-day coverage (FR-009) without fabricating attendance rows. | Reusing the existing dummy-checkin justification pollutes `checkins`, can't represent overlap or revoke cleanly, and ties the audit trail to a synthetic device. The link table keeps the attendance table truthful. |
