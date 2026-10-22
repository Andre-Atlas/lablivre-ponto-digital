---

description: "Task list for Medical Certificates & Absence Justification"
---

# Tasks: Medical Certificates & Absence Justification

**Input**: Design documents from `/specs/001-medical-certificate-absences/`

**Prerequisites**: plan.md ✅, spec.md ✅ (clarified 2026-10-09), research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: INCLUDED — the project constitution (Principle V, Test-First, NON-NEGOTIABLE)
mandates TDD. Test tasks are written first within each phase and MUST fail before the
implementation tasks that satisfy them.

**Organization**: Tasks are grouped by user story (US1–US3 from spec.md) so each story is an
independently testable, deployable increment.

**Clarifications applied** (2026-10-09): certificates apply to **ALUNO only** (FR-005a); a
certificate links every expected shift in range that **lacks a real present/late check-in**
(FALTA or already-JUSTIFICADO — FR-006); **both** CSV and Excel exports reflect certificates
and the **CSV branch is reworked** to enumerate expected shifts (FR-012); max document size is
**10 MB** (FR-017); unusually long periods get no special handling in v1.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3 (Setup, Foundational, Polish carry no story label)
- Exact file paths are included in every task.

## Path Conventions

Decoupled web app (per plan.md): backend hexagon under `backend/app/` with tests in
`backend/tests/`; frontend SPA under `web_admin/src/`. No new top-level projects.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Enable the one justified additive dependency and feature configuration.

- [x] T001 Add `python-multipart` to `backend/requirements.txt` and reinstall backend deps (required by FastAPI to parse `multipart/form-data` uploads — see plan Complexity Tracking).
- [x] T002 [P] Add certificate settings (`MAX_CERTIFICATE_SIZE_BYTES = 10 * 1024 * 1024` (10 MB), `ALLOWED_CERTIFICATE_CONTENT_TYPES = {application/pdf, image/jpeg, image/png}`) to `backend/app/config.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared domain, persistence, port, schema, and router skeleton that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 [P] Add `CertificateStatus` enum (`ACTIVE`, `REVOKED`) to `backend/app/domain/enums.py`.
- [x] T004 Write FAILING unit tests in `backend/tests/unit/test_certificate_domain.py` for: validation (end≥start; document present; content-type allowed; size ≤ 10 MB; subject must be `ALUNO`), and the pure coverage-expansion function (date range → expected `(data, turno, turno_referencia)` shifts via the turma grid; range with only non-class days → empty).
- [x] T005 Add `MedicalCertificate` and `CertificateDay` domain dataclasses to `backend/app/domain/models.py`.
- [x] T006 Implement the pure coverage-expansion domain function (expand `[periodo_inicio, periodo_fim]` to expected shifts via existing `TURNOS_ALUNOS` and `_DIA_SEMANA_MAP`) in `backend/app/domain/models.py` — makes T004 pass (depends on T005). NOTE: this function only enumerates expected shifts; filtering to shifts lacking a real present/late check-in happens in the use case (T014), which has DB access.
- [x] T007 [P] Add `MedicalCertificateModel` (BYTEA `documento`, metadata, status, audit cols, indexes) and `CertificateDayModel` (link cols, `ativo`, `turno_referencia`, `UniqueConstraint(certificate_id, turno_referencia)`, lookup index on `(user_id, turno_referencia, ativo)`) to `backend/app/adapters/persistence/orm_models.py` per data-model.md.
- [x] T008 [P] Define the `CertificateRepository` port ABC (`criar`, `buscar_por_id`, `listar`, `listar_dias_ativos_por_usuario`, `revogar`) in `backend/app/domain/ports/certificate_repository.py`.
- [x] T009 Create the Alembic migration creating `medical_certificates` and `certificate_days` (FKs, indexes, unique constraint) in `backend/alembic/versions/` and resolve the baseline/`down_revision` gap per research R6 (depends on T007).
- [x] T010 Implement the `CertificateRepository` adapter (all port methods, async SQLAlchemy) in `backend/app/adapters/persistence/certificate_repo_impl.py` (depends on T007, T008).
- [x] T011 [P] Create Pydantic schemas (`JustifiedDay`, `CertificateSummary`, `CertificateDetail`, revoke request) matching `contracts/medical-certificates.openapi.yaml` in `backend/app/api/schemas/certificate_schemas.py`.
- [x] T012 Scaffold `backend/app/api/v1/router_certificates.py` (prefix `/admin/certificados`, reuse `require_admin`), register it in `backend/app/main.py`, and create the `CertificateUseCase` skeleton (constructor + repo dependency) in `backend/app/application/certificate_use_case.py` (depends on T010, T011).

**Checkpoint**: Data layer, port, schemas, and router are in place; story implementation can begin.

---

## Phase 3: User Story 1 - Admin records a certificate and justifies covered absences (Priority: P1) 🎯 MVP

**Goal**: An admin uploads a certificate (document + contiguous period) for an `ALUNO`; on save, every expected shift in the period lacking a real present/late check-in becomes justified and linked to the certificate.

**Independent Test**: POST a certificate over a range containing 2 absent shifts → response 201 shows `status: ACTIVE` and exactly those 2 shifts in `dias`; present/late shifts and non-class days are excluded; an already-JUSTIFICADO shift in range is still linked; invalid submissions return 400 and store nothing.

### Tests for User Story 1 (write first, must FAIL) ⚠️

- [x] T013 [US1] Write FAILING integration tests for `POST /admin/certificados` in `backend/tests/integration/test_certificate_api.py`: happy path (201 + active `certificate_days` only for expected shifts in range lacking a real present/late check-in; shift with a present/late check-in excluded; already-JUSTIFICADO shift still linked; days with no expected shift excluded); validation (missing document / `periodo_fim` < `periodo_inicio` / unsupported type / >10 MB → 400; subject not `ALUNO` → 4xx per FR-005a); RBAC (non-admin → 403, missing token → 401).

### Implementation for User Story 1

- [x] T014 [US1] Implement `registrar` in `backend/app/application/certificate_use_case.py`: validate inputs (incl. subject is `ALUNO`, size ≤ 10 MB, content-type allowed), persist certificate bytes + metadata, expand coverage (T006), filter to expected shifts **lacking a real present/late check-in** (FALTA or already-JUSTIFICADO), and create active `CertificateDay` links for them (depends on T012).
- [x] T015 [US1] Implement `POST /admin/certificados` in `backend/app/api/v1/router_certificates.py` using `UploadFile` + `Form`, enforcing content-type/size from T002 and returning `CertificateDetail` (depends on T014).
- [x] T016 [P] [US1] Add the `recordCertificate` multipart client call (FormData, Bearer token) to `web_admin/src/services/api.ts`.
- [x] T017 [US1] Add the "Atestados" upload UI to `web_admin/src/pages/Dashboard.tsx` (modal: document picker + start/end dates + note; loading/empty/error states; Light/Dark; keyboard-accessible) (depends on T016).
- [x] T018 [US1] Add a Playwright E2E spec `web_admin/tests/e2e/certificados.spec.ts`: admin logs in, uploads a certificate for an ALUNO, sees the new certificate with its justified-day count.

**Checkpoint**: MVP — recording a certificate justifies and links covered absences end-to-end.

---

## Phase 4: User Story 2 - Trace which certificate justified an absence (Priority: P2)

**Goal**: From a certificate see all days it justified and open its document; justified days reference the certificate; **both** attendance exports (CSV and Excel) reflect certificate-backed justification.

**Independent Test**: GET a certificate → `dias` lists exactly its justified shifts; GET its document returns 200 for an admin and 403 for a student; **both** the CSV and Excel exports show those shifts as `JUSTIFICADO` (attributed to a certificate), others still `FALTA`.

### Tests for User Story 2 (write first, must FAIL) ⚠️

- [x] T019 [US2] Write FAILING integration tests in `backend/tests/integration/test_certificate_api.py` for `GET /admin/certificados` (list + `user_id`/`status` filters), `GET /admin/certificados/{id}` (detail with `dias[]`), and `GET /admin/certificados/{id}/documento` (admin 200 with correct content-type; student 403; unknown id 404).
- [x] T020 [US2] Write FAILING integration tests in `backend/tests/integration/test_export_with_certificates.py` asserting that **both** the CSV and the Excel export show a certificate-covered absent shift as `JUSTIFICADO` (attributed to the certificate) while uncovered absent shifts remain `FALTA`; include a case where a **future** covered shift becomes an absence after recording and is then reported `JUSTIFICADO` (FR-009).
- [x] T021 [US2] Implement `obter` (certificate + its days) and `listar` (with filters) in `backend/app/application/certificate_use_case.py`.
- [x] T022 [US2] Implement `GET /admin/certificados`, `GET /admin/certificados/{id}`, and `GET /admin/certificados/{id}/documento` (admin-only `StreamingResponse`) in `backend/app/api/v1/router_certificates.py` (depends on T021).
- [x] T023 [US2] Rework the attendance export in `backend/app/api/v1/router_admin.py` so **both** branches reflect certificates: extract the Excel branch's expected-shift (FALTA) enumeration into a shared helper, apply it to the **CSV branch** too (which today only dumps raw check-ins), and in both branches batch-load active `certificate_days` for the export window and emit `JUSTIFICADO` + certificate attribution for covered absent shifts instead of `FALTA` (depends on T010).
- [x] T024 [P] [US2] Add `listCertificates`, `getCertificate`, and `downloadCertificateDocument` client calls to `web_admin/src/services/api.ts`.
- [x] T025 [US2] Add the certificate list + detail + document view to `web_admin/src/pages/Dashboard.tsx`, and show the linked certificate on a justified day (depends on T024).

**Checkpoint**: US1 + US2 work independently; linkage is traceable both ways and visible in both exports.

---

## Phase 5: User Story 3 - Revoke a mistakenly recorded certificate (Priority: P3)

**Goal**: An admin revokes a certificate; shifts it solely justified revert to absence; the record and its history are retained.

**Independent Test**: Revoke a certificate linked to 2 absent shifts → status `REVOKED`, both revert to `FALTA` (unless another active certificate still covers them); re-revoking returns 409.

### Tests for User Story 3 (write first, must FAIL) ⚠️

- [x] T026 [US3] Write FAILING integration tests in `backend/tests/integration/test_certificate_api.py` for `POST /admin/certificados/{id}/revogar`: status → `REVOKED` with `revogado_por`/`revogado_em`; links deactivated; export shows reverted `FALTA`; overlap case (a second active certificate still covering the shift) keeps it `JUSTIFICADO`; already-revoked → 409.

### Implementation for User Story 3

- [x] T027 [US3] Implement `revogar` in `backend/app/application/certificate_use_case.py` (status flip + deactivate links via repo), including the already-revoked guard (depends on T010).
- [x] T028 [US3] Implement `POST /admin/certificados/{id}/revogar` in `backend/app/api/v1/router_certificates.py` (depends on T027).
- [x] T029 [P] [US3] Add the `revokeCertificate` client call to `web_admin/src/services/api.ts`.
- [x] T030 [US3] Add the revoke action (confirmation + status badge, no alert/confirm dialogs) to `web_admin/src/pages/Dashboard.tsx` (depends on T029).

**Checkpoint**: All three stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, verification, and hardening across the feature (constitution V & VI).

- [x] T031 [P] Align endpoint summaries/docstrings in `backend/app/api/v1/router_certificates.py` with `contracts/medical-certificates.openapi.yaml` so the generated OpenAPI (`/docs`) matches.
- [x] T032 [P] Update `README.md`, `docs/ARCHITECTURE.md`, and `CHANGELOG.md` to document medical certificates & certificate-backed justification (incl. the CSV export rework and ALUNO-only scope) (constitution Principle VI).
- [x] T033 Run `pytest --cov=app --cov-report=term-missing` from `backend/` and close gaps until new modules reach ≥80% coverage.
- [ ] T034 Execute `quickstart.md` Scenarios 1–5 (incl. the both-exports check in Scenario 2) against the docker-compose stack and confirm expected outcomes.
- [x] T035 [P] Security pass: confirm every certificate endpoint is behind `require_admin`, document download is admin-only, file type/size are enforced, and no secrets were added (constitution Principle IV).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup — **BLOCKS all user stories**.
- **User Stories (Phases 3–5)**: all depend on Foundational; then proceed in priority order (P1 → P2 → P3) or in parallel if staffed.
- **Polish (Phase 6)**: depends on the desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: depends only on Foundational. Delivers the MVP on its own.
- **US2 (P2)**: depends on Foundational; builds on data created by US1 but is independently testable (seed a certificate directly). T023 (export rework) and T025 (justified-day reference) read US1's data.
- **US3 (P3)**: depends on Foundational; independently testable (seed a certificate, then revoke).

### Within Each User Story

- Test task(s) first and failing → use case → endpoint → frontend client → frontend UI/E2E.
- Models before services; services before endpoints; backend before the UI that calls it.

### Parallel Opportunities

- Setup: T002 [P] alongside T001.
- Foundational: T003, T007, T008, T011 [P] (distinct files); T006 waits on T005, T009 on T007, T010 on T007+T008, T012 on T010+T011.
- Per story: the `api.ts` client task ([P]) can run alongside backend tasks (different file) — T016, T024, T029.
- With a team: once Foundational is done, US1/US2/US3 can be split across developers. Note the three frontend tasks all edit `web_admin/src/pages/Dashboard.tsx` and the three client tasks all edit `web_admin/src/services/api.ts` — serialize those cross-story edits to avoid conflicts.

---

## Parallel Example: Foundational Phase

```bash
# After Setup, launch the independent foundational building blocks together:
Task: "T003 Add CertificateStatus enum in backend/app/domain/enums.py"
Task: "T007 Add ORM models in backend/app/adapters/persistence/orm_models.py"
Task: "T008 Define CertificateRepository port in backend/app/domain/ports/certificate_repository.py"
Task: "T011 Create Pydantic schemas in backend/app/api/schemas/certificate_schemas.py"
```

## Parallel Example: User Story 1

```bash
# The frontend client call can proceed while the backend endpoint is built (different files):
Task: "T016 Add recordCertificate client call in web_admin/src/services/api.ts"
# ...in parallel with backend T014/T015 (backend files).
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1: Setup → 2. Phase 2: Foundational (CRITICAL, blocks everything) → 3. Phase 3: US1.
4. **STOP and VALIDATE**: record a certificate and confirm covered absences are justified and linked.
5. Deploy/demo — this alone replaces the manual per-day justification for medical reasons.

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. US1 → test independently → deploy (MVP: record + justify + link).
3. US2 → test independently → deploy (traceability + both-export reflection).
4. US3 → test independently → deploy (revoke + revert).

### Parallel Team Strategy

After Foundational completes, Developer A takes US1, B takes US2, C takes US3; serialize the
shared `Dashboard.tsx` and `api.ts` edits. Stories integrate independently.

---

## Notes

- [P] = different files, no incomplete-task dependency.
- [Story] label maps each task to its user story for traceability.
- Verify every test fails before implementing (constitution Principle V).
- Link rule (FR-006): link every expected shift in range lacking a real present/late check-in (FALTA or already-JUSTIFICADO); never link a shift that has a real present/late check-in. Do NOT create dummy `JUSTIFICADO` check-ins for certificates — coverage is the `certificate_days` link (research R1); the legacy `justificar` endpoint is left untouched.
- Export (FR-012): both CSV and Excel must reflect certificates; the CSV branch is reworked to enumerate expected ALUNO shifts via a helper shared with the Excel branch.
- Document bytes live in Postgres (BYTEA, ≤ 10 MB), never on pod disk (constitution Principle III).
- Commit after each task or logical group; stop at any checkpoint to validate a story independently.
