<!--
Sync Impact Report
==================
Version change: TEMPLATE (unversioned) → 1.0.0
Rationale: First concrete ratification of the Ponto Digital constitution. MAJOR bump
           from an empty template to a fully defined governance document.

Modified principles: N/A (initial definition)
Added principles:
  - I. Stack Stability (NON-NEGOTIABLE)
  - II. Contract-First & Decoupled Services
  - III. Async & Stateless by Default
  - IV. Security & RBAC by Design
  - V. Test-First Quality Gates (NON-NEGOTIABLE)
  - VI. Impeccable UX & Living Documentation
Added sections:
  - Locked Technology Stack (Section 2)
  - Development Workflow & Quality Gates (Section 3)
Removed sections: None

Templates requiring updates:
  - .specify/templates/plan-template.md ........ ✅ aligned (Constitution Check gate is
    generic and resolved per-feature; no outdated references)
  - .specify/templates/spec-template.md ........ ✅ aligned (no stack/principle coupling)
  - .specify/templates/tasks-template.md ....... ✅ aligned (story-driven; no principle drift)
  - .claude/skills/speckit-*/ .................. ✅ reviewed (agent-agnostic guidance)

Runtime guidance reviewed:
  - README.md, ARCHITECTURE.md, docs/ARCHITECTURE.md, AGENTS.md ... ✅ consistent with
    principles (stack, decoupling, RBAC, async/stateless, test gate, impeccable UX,
    living docs all originate from these docs)

Follow-up TODOs: None. RATIFICATION_DATE set to first fill-in date (2026-10-09).
-->

# Ponto Digital — LabLivre UnB Constitution

## Core Principles

### I. Stack Stability (NON-NEGOTIABLE)

The platform evolves through NEW FEATURES, never through stack churn. The technology
stack defined in the "Locked Technology Stack" section is fixed for day-to-day work.

- New features MUST be built with the existing languages, frameworks, and libraries
  already present in the stack. Reuse before you add.
- Introducing a new language, framework, runtime, database engine, or a heavyweight
  new dependency is a stack change and is PROHIBITED without a constitutional
  amendment (see Governance). "It would be nicer in X" is not sufficient cause.
- Minor, additive dependencies that stay within an existing layer's conventions
  (e.g., a focused Python library on the FastAPI backend, a small React utility) MAY
  be added if they are justified in the feature plan, actively maintained, and do not
  replace or duplicate an existing capability.
- Upgrades of existing dependencies are allowed and encouraged for security and
  maintenance; they MUST NOT be used as a backdoor to swap the architecture.

**Rationale**: This platform's value is operational stability for a university lab, not
technical novelty. A locked stack keeps the system maintainable by a rotating student
team, keeps deploys predictable, and forces design energy into features users feel.

### II. Contract-First & Decoupled Services

No code is written before its contract exists, and the services stay independent.

- The API contract (endpoint shape, request/response Pydantic models, status codes,
  auth scope) MUST be defined before backend or frontend implementation begins.
- Frontend (`web_admin`), backend (`backend`), and the desktop client (`desktop_app`)
  are separately deployable units that communicate ONLY over the versioned REST API
  (`/api/v1/*`) with JWT bearer auth. No shared in-process state, no hidden coupling.
- Business rules MUST be isolated from transport (FastAPI) and persistence
  (SQLAlchemy) details, so domain logic is testable without a running server or DB.

**Rationale**: Decoupling is what lets the same backend serve Web and Desktop, lets the
frontend deploy to Vercel while the backend runs on Render or Kubernetes, and keeps
contract changes visible and reviewable rather than silently breaking a client.

### III. Async & Stateless by Default

The compute layer is disposable; the database is the only source of truth.

- All backend database access MUST be asynchronous (async SQLAlchemy over asyncpg).
  Blocking I/O in request paths is prohibited.
- Backend and frontend processes MUST remain stateless: no session state, uploaded
  files, or durable data stored on a pod/container's local disk. Persistent state
  lives exclusively in the managed PostgreSQL database.
- Authentication is stateless JWT (bearer token); server-side sessions are prohibited.

**Rationale**: Statelessness is what makes pods destroyable, scalable, and recreatable
without data loss, and async DB access is what lets a single service handle hundreds of
concurrent check-ins without blocking.

### IV. Security & RBAC by Design

Access control and data protection are built in, not bolted on.

- Every protected endpoint MUST enforce one of the four roles — `SUPER_ADMIN`,
  `ADMIN`, `STAFF`, `ALUNO` — server-side. The frontend hiding a control is never the
  access control; the backend is the authority.
- Role checks follow least privilege: a feature grants the narrowest role that works.
- Passwords MUST be stored only as bcrypt hashes. Secrets (JWT keys, DB URLs) MUST come
  from environment/config, never be committed to the repository.
- All request and response payloads at the API boundary MUST be validated by Pydantic
  models; untyped/unvalidated input into business logic is prohibited.
- Containers MUST run as non-root users, per the cloud-native hardening already in the
  Dockerfiles.

**Rationale**: The system holds students' attendance and identity records under
university compliance expectations; a single missing server-side role check or a
committed secret is a reportable incident.

### V. Test-First Quality Gates (NON-NEGOTIABLE)

Tests precede implementation and block merges.

- New backend features and bug fixes follow TDD: write the failing test, confirm it
  fails, then implement to green. Backend unit coverage MUST stay at or above 80%.
- Contract changes and inter-service behavior MUST have integration tests; user-facing
  frontend flows MUST have E2E coverage (Playwright).
- The test gate is blocking: a broken test or a regression halts the pipeline. Advance
  only on explicit, documented passing results — never on an unverified "should work".

**Rationale**: A rotating student team cannot hold the whole system in their heads;
tests are the memory that prevents each new feature from silently breaking attendance
calculation, exports, or auth for everyone else.

### VI. Impeccable UX & Living Documentation

What ships looks finished, and the docs never lie.

- Frontend components MUST handle loading (skeleton), empty, error, and accessibility
  (keyboard focus, labels) states, support automatic Light/Dark themes, and avoid the
  generic "AI template" look. Partial, state-less UI is not done.
- Every change that alters an API, a data model, a role, or user-facing behavior MUST
  ship with its documentation updated in the same change: OpenAPI/Swagger, README,
  ARCHITECTURE/docs, and CHANGELOG. Stale docs are treated as a defect.

**Rationale**: Users and future maintainers judge the platform by its interface and its
docs; polish and accurate living documentation are what make the system trustworthy and
hand-off-able.

## Locked Technology Stack

This section defines the stack referenced by Principle I. Changes here require a
constitutional amendment.

- **Backend** (`backend/`): Python + FastAPI, async SQLAlchemy 2.x over asyncpg,
  Pydantic for validation, Alembic for migrations, JWT via python-jose, password
  hashing via bcrypt/passlib, pytest for tests. Served in production by Gunicorn with
  Uvicorn workers.
- **Database**: PostgreSQL, hosted as a managed service (Supabase / Neon / RDS).
  Stateful data lives here only.
- **Frontend** (`web_admin/`): React 19 + TypeScript, bundled with Vite, styled with
  Tailwind CSS, icons via Lucide, HTTP via axios, routing via react-router-dom. Linting
  with oxlint; E2E with Playwright.
- **Desktop client** (`desktop_app/`): Python + Flet, packaged as native standalone
  binaries for Windows, macOS, and Linux.
- **Orchestration & Deploy**: Docker + docker-compose for local/dev parity; Kubernetes
  manifests (`k8s/`) for production; alternative hosting on Vercel (frontend) + Render
  (backend) is supported and MUST remain supported.
- **Integration surfaces** already in use (Excel export via openpyxl, Google Sheets via
  gspread) are part of the stack and may be extended within their existing libraries.

Adding to this list, removing from it, or replacing any entry is a stack change under
Principle I and triggers the amendment process.

## Development Workflow & Quality Gates

The team (human or agent squad) follows the pipeline defined in `AGENTS.md`:

1. **Scope & Contract**: The requirement is scoped and its API contracts, data model,
   and interfaces are defined BEFORE any implementation (Principle II). No code without
   a contract.
2. **Build**: Backend (domain + API + schemas) and frontend (screens + components) are
   implemented against the agreed contract, in their respective decoupled services.
3. **Test (blocking gate)**: Backend TDD + integration and frontend E2E + visual/a11y
   checks run. Any failure or regression blocks progress (Principle V).
4. **Integration audit**: Front–back integration is verified on a branch before merge.
5. **Document**: OpenAPI, README, architecture docs, and CHANGELOG are synchronized
   with the change (Principle VI).
6. **Merge & Deploy**: Reviewed PR is merged and deployed safely (canary/rollout aware).

Every PR review MUST confirm: stack unchanged (or amendment linked), contracts honored,
async/stateless preserved, RBAC + validation present, tests green at required coverage,
UX states complete, and docs updated. Any deliberate deviation MUST be recorded in the
feature plan's Complexity Tracking with its justification and the simpler rejected
alternative.

## Governance

This constitution supersedes other development practices for the Ponto Digital
platform. Where a skill, agent definition, or habit conflicts with it, the constitution
wins.

- **Amendments**: Any change to a principle or to the Locked Technology Stack MUST be
  proposed in writing (PR editing this file), justified against the platform's goals,
  include a migration/impact note, and be approved by the project lead before merge.
- **Versioning** (semantic): MAJOR for backward-incompatible principle removals or
  redefinitions; MINOR for a new principle/section or materially expanded guidance;
  PATCH for clarifications and wording. The version line below is updated on every
  amendment, along with the Last Amended date and the Sync Impact Report at the top.
- **Compliance**: Constitution compliance is verified at PR review and at the plan-stage
  Constitution Check gate. Non-compliant work does not merge. Complexity or deviation
  that cannot be removed MUST be explicitly justified and recorded.
- **Runtime guidance**: `AGENTS.md`, `README.md`, `ARCHITECTURE.md`, and
  `docs/ARCHITECTURE.md` provide operational detail and MUST stay consistent with this
  constitution; on conflict, this document is authoritative.

**Version**: 1.0.0 | **Ratified**: 2026-10-09 | **Last Amended**: 2026-10-09
