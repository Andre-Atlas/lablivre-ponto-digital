# Quickstart & Validation: Medical Certificates & Absence Justification

This guide proves the feature end-to-end. It references [data-model.md](./data-model.md) and
[contracts/medical-certificates.openapi.yaml](./contracts/medical-certificates.openapi.yaml);
it does not duplicate schema or include implementation code.

## Prerequisites

- The platform running locally via Docker Compose (see root `README.md`):
  ```bash
  docker-compose build && docker-compose up -d
  ```
  Backend on `http://localhost:8000` (Swagger at `/docs`), frontend on `http://localhost:5173`.
- An administrator account (role `ADMIN` or `SUPER_ADMIN`). Obtain a JWT via
  `POST /api/v1/auth/admin-login`; export it: `export TOKEN=<access_token>`.
- At least one student (`tipo = ALUNO`) with a `turma_ou_equipe` that has expected shifts in
  `TURNOS_ALUNOS`, and no check-ins on the days you will cover (so those shifts are absences).
- Apply the new Alembic migration before running:
  ```bash
  cd backend && alembic upgrade head
  ```

## Backend checks (run from `backend/`)

```bash
# Unit + integration tests for this feature (written test-first)
pytest tests/unit/test_certificate_domain.py \
       tests/integration/test_certificate_api.py \
       tests/integration/test_export_with_certificates.py -v

# Coverage gate (constitution Principle V: >= 80%)
pytest --cov=app --cov-report=term-missing
```

Expected: all tests pass; coverage for new modules ≥ 80%.

## Scenario 1 — Record a certificate and justify covered absences (US1, P1)

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/certificados \
  -H "Authorization: Bearer $TOKEN" \
  -F "user_id=<STUDENT_UUID>" \
  -F "periodo_inicio=2026-10-05" \
  -F "periodo_fim=2026-10-09" \
  -F "observacao=Atestado 5 dias" \
  -F "documento=@./atestado.pdf;type=application/pdf"
```

**Expected (201)**: a `CertificateDetail` with `status: ACTIVE` and a `dias` array listing
exactly the expected shifts in `2026-10-05..2026-10-09` that were absences for the student.
Days in range with no expected shift (e.g., weekend) do **not** appear.

**Negative checks** (each returns 400, nothing stored):
- Omit `documento` → "document required".
- `periodo_fim=2026-10-04` with `periodo_inicio=2026-10-05` → "end before start".
- Upload a `.txt` or a >10 MB file → "unsupported type / too large".

## Scenario 2 — Verify the link both ways and in the export (US1 + US2, P1/P2)

```bash
# Certificate -> days it justified
curl -s http://localhost:8000/api/v1/admin/certificados/<CERT_UUID> \
  -H "Authorization: Bearer $TOKEN"        # dias[] lists every justified shift

# BOTH exports now show those shifts as JUSTIFICADO (not FALTA)
curl -s "http://localhost:8000/api/v1/admin/export/checkins?format=csv&ano=2026&mes=10" \
  -H "Authorization: Bearer $TOKEN" -o relatorio.csv
curl -s "http://localhost:8000/api/v1/admin/export/checkins?format=excel&ano=2026&mes=10" \
  -H "Authorization: Bearer $TOKEN" -o relatorio.xlsx
```

**Expected**: in **both** `relatorio.csv` and `relatorio.xlsx`, the covered shifts for the
student show status `JUSTIFICADO` (attributable to a medical certificate), while uncovered
absent shifts still show `FALTA`. (Note: the CSV export is reworked to enumerate expected
`ALUNO` shifts like the Excel report, rather than dumping raw check-ins.)

## Scenario 3 — Future-day coverage (US1 acceptance #5, FR-009)

Record a certificate whose range includes a **future** class day on which the student has no
check-in. Let that day pass (or simulate by choosing a just-elapsed day with no check-in),
re-run the export from Scenario 2.

**Expected**: the once-future day is reported `JUSTIFICADO` and linked to the same certificate,
with no manual action taken after recording.

## Scenario 4 — Revoke (US3, P3, FR-013/FR-016)

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/certificados/<CERT_UUID>/revogar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"motivo":"documento inválido"}'
```

**Expected (200)**: `status: REVOKED`, `revogado_em`/`revogado_por` set. Re-running the export
shows the previously justified shifts back as `FALTA` — **unless** another active certificate
still covers them (overlap), in which case they remain `JUSTIFICADO`.

## Scenario 5 — RBAC & document confidentiality (FR-005, FR-015)

```bash
# Non-admin (student) token must be rejected on every certificate endpoint
curl -s -o /dev/null -w "%{http_code}\n" \
  http://localhost:8000/api/v1/admin/certificados -H "Authorization: Bearer $STUDENT_TOKEN"
# Expected: 403

# Document download requires an admin token
curl -s -o /dev/null -w "%{http_code}\n" \
  http://localhost:8000/api/v1/admin/certificados/<CERT_UUID>/documento \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 (admin); 403 with a student token
```

## Frontend check (Dashboard, Playwright E2E)

1. Log in as an admin at `http://localhost:5173`.
2. Open the student's record → **Atestados** section → upload a PDF with a start/end date.
3. Confirm the UI shows loading, then the new certificate with its justified-day count, in
   Light and Dark themes, with keyboard-accessible controls.
4. Confirm a justified day in the attendance view names the certificate and can open the
   document; revoke the certificate and confirm the day reverts.

**Expected**: the E2E spec passes; no console errors; empty/error states render (e.g., a
student with no certificates shows an empty state, a failed upload shows an inline error).

## Done when

- All backend tests pass with ≥ 80% coverage on new modules.
- Scenarios 1–5 behave as described against a running stack.
- The Playwright E2E for the admin certificate flow passes.
- OpenAPI (`/docs`), README, ARCHITECTURE, and CHANGELOG are updated (constitution VI).
