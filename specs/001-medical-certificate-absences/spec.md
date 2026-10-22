# Feature Specification: Medical Certificates & Absence Justification

**Feature Branch**: `001-medical-certificate-absences`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: "Alongside with the frequence, create a feature to gather the medical certificate and justificate absences. One medical certificate can justify the absence of more than one day. I want that when there is some absence, the medical keep linked to the day that the student is absent."

## Clarifications

### Session 2026-10-09

- Q: Which users can a medical certificate be recorded for? → A: ALUNO only (students). STAFF are out of scope, since attendance faltas/justified status are computed only for ALUNO.
- Q: Which attendance export(s) must show certificate-justified absences as JUSTIFICADO? → A: Both CSV and Excel. The CSV export (currently a raw check-in dump) must be extended to enumerate expected shifts and show FALTA/JUSTIFICADO consistently with the Excel report.
- Q: When a certificate covers a shift that was already justified manually, should it still link to that day? → A: Yes. A certificate-day link is created for every expected shift in range that lacks a real present/late check-in (FALTA or already-JUSTIFICADO); the day stays justified and the certificate origin is recorded.
- Q: How should the system handle an unusually long certificate period? → A: No special handling in v1. Accept any valid range (end >= start); no length warning or cap. Deferred to a later version.
- Q: What is the maximum allowed certificate document size? → A: 10 MB. Uploads larger than 10 MB are rejected with a clear message.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin records a certificate and justifies every absent day it covers (Priority: P1)

An administrator receives a student's medical certificate (in person, by e-mail, etc.),
opens the student's record, and uploads the certificate document while entering the
period it covers (the days of rest it indicates). On save, every mandatory working day
within that period on which the student has an absence is marked as justified, and each
of those days is permanently linked to the certificate so the origin of the
justification is always traceable.

**Why this priority**: This is the whole intent of the feature — gather the certificate
and, in one action, justify the one-or-more absent days it covers while keeping the
certificate linked to each day. It is the minimum usable version and delivers the
business outcome on its own.

**Independent Test**: An admin uploads a certificate for a student covering a 3-day range
in which the student has 2 absences; on save, both absent days change to "justified" and
each shows the linked certificate, while any present or non-required day in the range is
untouched.

**Acceptance Scenarios**:

1. **Given** a student with absences on 3 consecutive mandatory days, **When** an admin
   records a certificate with a document covering those dates, **Then** all 3 days become
   "justified" and each is linked to that certificate.
2. **Given** an admin recording a certificate, **When** they omit the document or the
   covered period, **Then** the action is rejected with a clear message and nothing is
   stored.
3. **Given** an admin recording a certificate, **When** the end date is before the start
   date, **Then** the action is rejected with a validation message.
4. **Given** a covered period that includes days where the student was present or where
   attendance was not required, **When** the admin saves the certificate, **Then** only
   the actual absent mandatory days are justified and linked; the other days are unchanged.
5. **Given** a certificate already recorded, **When** a mandatory day inside its covered
   period later becomes an absence (the day elapses with no check-in), **Then** that day
   is automatically justified and linked to the same certificate.

---

### User Story 2 - Trace which certificate justified an absence (Priority: P2)

From any justified day, an administrator can see which certificate justified it and open
the underlying document. Conversely, from a certificate they can see every day it
justified. Attendance reports and exports reflect the certificate-backed justification so
the audit trail is visible where absences are reviewed.

**Why this priority**: The user explicitly requires the certificate to stay linked to the
absent day. Traceability in both directions — including in the existing reports — is what
makes the linkage useful rather than merely stored.

**Independent Test**: For a day justified by a certificate, open the day's detail and
confirm it names the certificate and lets the document be viewed; open the certificate and
confirm it lists exactly the days it justified; generate the attendance export and confirm
those days show as justified by a medical certificate.

**Acceptance Scenarios**:

1. **Given** a day justified by a certificate, **When** an admin views that day's detail,
   **Then** the linked certificate (identifier, covered period, document) is shown.
2. **Given** a certificate linked to several days, **When** an admin opens the certificate,
   **Then** every justified day is listed.
3. **Given** justified days in a reporting period, **When** an attendance report is
   generated, **Then** those days appear as justified and indicate they were justified by a
   medical certificate.

---

### User Story 3 - Revoke a mistakenly recorded certificate (Priority: P3)

An administrator who recorded a certificate in error (wrong student, wrong period, or an
invalid document) revokes it. Every day that was justified solely by that certificate
reverts to its underlying state (absence) and the link is removed, keeping attendance
records accurate. The certificate record and its history are retained for audit.

**Why this priority**: Corrects mistakes and prevents a bad certificate from permanently
masking absences. Important for integrity but not needed for the first usable version.

**Independent Test**: Revoke a certificate that justified two days; both days revert to
"absence" and no longer reference the certificate, while the certificate remains visible as
"revoked".

**Acceptance Scenarios**:

1. **Given** a recorded certificate linked to 2 absent days, **When** an admin revokes it,
   **Then** both days return to "absence" and the certificate shows status "revoked".
2. **Given** a revoked certificate, **When** an admin views it, **Then** its history
   (recorded, revoked, by whom and when) is retained.

---

### Edge Cases

- **Overlapping certificates**: Two certificates cover the same absent day. The day stays
  justified; the link records which certificate(s) apply, and revoking one while another
  still covers the day keeps the day justified.
- **Certificate covering non-working days only**: No absences exist to justify; the
  certificate is recorded but links to zero days (shown as covering no eligible days).
- **Certificate recorded before the absence occurs** (future-dated rest period): The
  certificate is stored and, as covered days elapse into absences, they are justified and
  linked automatically.
- **Day already justified manually** that a certificate also covers: the day stays
  justified and the certificate link is added so the document-backed origin is recorded.
- **Document too large or an unsupported file type**: the action is rejected with a clear
  message before anything is stored.
- **Certificate period that is unusually long** (e.g., months): accepted as-is in v1 — any
  valid range (end ≥ start) is allowed, with no length warning or cap (deferred to a later
  version).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let an administrator record a certificate for a specific student
  with a required attached document and a covered period, storing who recorded it and when.
- **FR-002**: System MUST support a certificate covering a contiguous period of more than
  one day, so a single certificate can justify multiple absent days.
- **FR-003**: System MUST validate the record, rejecting it when the document is missing,
  the covered period is missing, or the end date is earlier than the start date.
- **FR-004**: System MUST treat recording a certificate as authoritative at the moment it
  is saved (no separate approval step), because only administrators can record one; the
  save itself applies the justification.
- **FR-005**: System MUST restrict recording, viewing, revoking, and managing certificates
  to administrators; students do not submit or manage certificates themselves.
- **FR-005a**: System MUST allow a certificate to be recorded only for a student of type
  `ALUNO`. STAFF users are out of scope for certificates (their attendance has no falta
  computation to justify).
- **FR-006**: On save, System MUST identify every expected mandatory working shift within the
  covered period for which the student has **no real present/late check-in** (i.e., the shift
  is a FALTA, or was already JUSTIFICADO), mark each as justified, and link each such shift to
  the certificate. Shifts with a real present/late check-in are excluded.
- **FR-007**: System MUST NOT alter days within the covered period where the student was
  present or where attendance was not required.
- **FR-008**: System MUST keep the certificate linked to each absent day it justified for as
  long as the justification stands, so the origin of every justified day is traceable.
- **FR-009**: System MUST apply a certificate's justification to covered days whose absence
  is determined after the certificate is recorded (e.g., a covered day that later elapses
  without a check-in), linking them to the same certificate.
- **FR-010**: System MUST let an administrator, starting from a justified day, see and open
  the certificate (and its document) that justified it.
- **FR-011**: System MUST let an administrator, starting from a certificate, see every day
  it justified.
- **FR-012**: System MUST reflect certificate-backed justifications in **both** the CSV and
  the Excel attendance exports, showing affected days as justified and attributable to a
  medical certificate. The CSV export (today a raw check-in dump) MUST be extended to
  enumerate expected shifts and report FALTA/JUSTIFICADO consistently with the Excel report.
- **FR-013**: System MUST allow an administrator to revoke a recorded certificate, reverting
  days justified solely by it back to absence and removing the link, while retaining the
  certificate record and its history for audit.
- **FR-014**: System MUST retain an audit history for each certificate (recorded and
  revoked — with actor and timestamp).
- **FR-015**: System MUST restrict viewing of a certificate's document to administrators,
  since it contains sensitive health information.
- **FR-016**: System MUST handle a day covered by more than one certificate by keeping the
  day justified as long as at least one covering certificate remains valid.
- **FR-017**: System MUST accept the document as a PDF or common image (JPEG, PNG) up to a
  maximum of 10 MB, and reject other types or files larger than 10 MB with a clear message.

### Key Entities *(include if feature involves data)*

- **Medical Certificate**: A document-backed justification recorded by an administrator for
  a student. Attributes: the student it applies to, covered period (start and end date,
  contiguous), attached document, optional note/reason, status (active, revoked), the admin
  who recorded it, and timestamps for recording and revocation. One certificate relates to
  many justified days.
- **Justified Day Link**: The association between a specific absent day of a student and the
  certificate that justifies it. Represents the persistent link the user requires; a day may
  relate to one (or more, in overlap cases) certificate(s), and a certificate relates to many
  days.
- **Absence / Attendance Day** (existing concept): A mandatory working day for a student
  classified as present, late, absence, or justified. This feature adds the ability for a day
  classified as absence to become justified via a linked certificate. (Reuses the platform's
  existing attendance/absence computation.)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An administrator can record a medical certificate for a student, document
  included, in under 3 minutes.
- **SC-002**: Recording one certificate justifies all covered absent days in a single action,
  with no need to justify days one by one.
- **SC-003**: 100% of days justified by a certificate display the certificate that justified
  them, and every certificate lists 100% of the days it justified.
- **SC-004**: Attendance reports show certificate-justified days as justified (not as
  absences) in 100% of cases within a reviewed period.
- **SC-005**: Revoking a certificate reverts every day it solely justified back to absence
  with no residual links remaining.
- **SC-006**: Locating the document behind any justified absence takes no more than two steps
  from the day or the report.
- **SC-007**: Reduce manual one-by-one absence justifications for medical reasons by at least
  70% once certificates are adopted.

## Assumptions

- This feature is built **alongside the existing frequency/attendance system** and reuses its
  working-day grid and absence / justified classification rather than introducing a parallel
  attendance model.
- Per the clarified decisions: **only administrators record and manage certificates**;
  students do not self-submit. Because the recording admin is the trusted authority, the
  certificate applies its justification on save, with **no separate approval step**.
- "More than one day" is a **contiguous covered period** (start date to end date, inclusive);
  justification applies only to the mandatory working days with absences inside that period.
- Accepted documents are PDF, JPEG, or PNG up to a maximum of 10 MB; larger or other formats
  are rejected.
- A certificate justifies only the subject student's own days; it does not affect other
  students.
- The attached document contains sensitive health data and is treated as confidential,
  visible only to administrators.
- Existing attendance reports/exports are the surface where justified days reflect the
  certificate; a brand-new reporting system is out of scope.
- Student-facing notifications (e.g., informing a student when a certificate is recorded) are
  out of scope for the first version unless later requested.
- The existing authentication and user-profile systems are reused; login is unchanged.
