# Feature Specification: Weekly Learning-Outcome Evaluation

**Feature Branch**: `002-weekly-lo-evaluation`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Weekly evaluation of students against learning outcomes (LOs). Mentors evaluate each student once per week, assigning a level 1–4 per LO plus a comment, with the form pre-filled from the student's last known levels; admins manage the LO catalog; a per-week dashboard shows assessed vs pending, per-mentor counts, a level heatmap per LO, and regressions vs the previous week; weekly per-student levels and comments export via the existing CSV/Excel engine. Additive to lablivre-ponto-digital, reusing the existing User model and locked stack. Out of scope: AI summaries and PDF generation."

## Clarifications

### Session 2026-10-13

- Q: How are mentors assigned to the students they can evaluate? → A: Reuse the existing single turma field (`turma_ou_equipe`). A mentor evaluates students in their one turma; no new mentor–turma mapping in v1.
- Q: When two different mentors evaluate the same student in the same week, what happens? → A: One evaluation per student/week; a later save updates each outcome's level (last write wins, change recorded) and each mentor's comment is kept separately.
- Q: Can students see their own evaluation results in v1? → A: No — evaluations, dashboard, and reports are staff-only (mentors/admins). A student-facing view may be added later.
- Q: What counts as a student being "assessed" in a week? → A: A student is "assessed" once at least one LO level is recorded for that week; a comment alone does not mark the student assessed. The per-mentor tally counts students for whom that mentor set ≥ 1 level.
- Q: When a student changes turma mid-program, which turma do dashboard/report use? → A: Not applicable in v1 — turma membership is assumed stable for the program's duration, so the evaluation's turma and the student's current turma are always equal. Mid-program turma changes are out of scope for v1.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mentor records a student's weekly LO evaluation (Priority: P1)

A mentor opens the evaluation form for a student in a given week. The form lists the active
learning outcomes, each pre-filled with that student's most recent level from an earlier week
(blank if never assessed). The mentor sets or adjusts a level from 1 to 4 for the outcomes
they are assessing, writes an optional qualitative comment, and saves. The evaluation is
recorded for that student and week and attributed to the mentor.

**Why this priority**: Capturing the weekly assessment is the whole point of the feature and
the smallest slice that delivers value — without it there is nothing to show on a dashboard or
in a report. It is independently demonstrable on its own.

**Independent Test**: With an active LO catalog and a student, a mentor submits levels for a
week; reopening the form for that student/week shows the saved levels and comment, and the
next week's form pre-fills from them.

**Acceptance Scenarios**:

1. **Given** an active LO catalog and a student with no prior evaluations, **When** a mentor
   submits levels (1–4) for some outcomes plus a comment for week 3, **Then** the evaluation
   is stored for that student/week, attributed to the mentor, and is retrievable.
2. **Given** a student evaluated in week 3, **When** a mentor opens the week 4 form for that
   student, **Then** each outcome is pre-filled with the student's week-3 level.
3. **Given** a mentor submitting an evaluation, **When** any level is outside 1–4 or references
   an outcome not in the catalog, **Then** the submission is rejected with a clear message and
   nothing is stored.
4. **Given** a mentor who is not assigned to the student's turma, **When** they try to submit an
   evaluation for that student, **Then** the submission is rejected.

---

### User Story 2 - Administrator manages the LO catalog (Priority: P2)

An administrator maintains the list of learning outcomes used in evaluations: adding an
outcome (number, name, description), editing it, and deactivating one that is no longer used.
Evaluation forms and dashboards reflect the active catalog.

**Why this priority**: The catalog defines what every evaluation references. It is needed to
set up and evolve the program, but evaluations can run against a seeded catalog, so it ranks
just below the capture flow.

**Independent Test**: An admin adds an outcome and deactivates another; the evaluation form
then lists the newly added outcome and no longer offers the deactivated one, while historical
evaluations referencing the deactivated outcome remain intact.

**Acceptance Scenarios**:

1. **Given** an admin, **When** they add an outcome with a number, name, and description,
   **Then** it appears as an active outcome available for evaluation.
2. **Given** an outcome with historical evaluations, **When** an admin deactivates it, **Then**
   it is no longer offered on new evaluation forms but past evaluations that referenced it are
   preserved and still shown in reports.
3. **Given** a non-administrator, **When** they attempt to create or edit an outcome, **Then**
   the action is rejected.

---

### User Story 3 - Weekly dashboard for a turma (Priority: P2)

A mentor or administrator views a dashboard for a turma and week showing: how many students
were assessed versus still pending, how many evaluations each mentor recorded, a heatmap of
levels per outcome across the turma, and regressions — students whose level on an outcome
dropped compared with the previous week.

**Why this priority**: Turns captured data into the oversight the program needs (who still
needs assessing, where the cohort stands, who regressed). Valuable but depends on US1 data.

**Independent Test**: With several students evaluated for a week (and one left pending, and one
whose level dropped vs the prior week), the dashboard shows the correct assessed/pending counts,
per-mentor tallies, the level heatmap, and flags the regression.

**Acceptance Scenarios**:

1. **Given** a turma where some students are evaluated for the week and some are not, **When**
   a user opens the dashboard for that week, **Then** it shows the assessed count, the pending
   count, and which students are pending.
2. **Given** evaluations recorded by different mentors, **When** the dashboard loads, **Then**
   it shows the number of students each mentor assessed that week.
3. **Given** a student whose level on an outcome is lower than the previous week, **When** the
   dashboard loads, **Then** that student/outcome is flagged as a regression.

---

### User Story 4 - Export a weekly report (Priority: P3)

A mentor or administrator exports a report for a turma and week containing, per student, their
level on each outcome and the week's comments, using the platform's existing spreadsheet export
(CSV/Excel).

**Why this priority**: Enables sharing and record-keeping outside the app. Useful but the
in-app dashboard already surfaces the data, so it is the lowest priority of the four.

**Independent Test**: For a week with evaluations, generating the export produces a file listing
each student with their per-outcome levels and comments; pending students appear without levels.

**Acceptance Scenarios**:

1. **Given** a week with evaluations, **When** a user exports the weekly report for the turma,
   **Then** the file lists each student with their level per outcome and the week's comments.
2. **Given** a student not yet evaluated that week, **When** the report is generated, **Then**
   that student appears marked as pending (no levels).

---

### Edge Cases

- **Re-evaluation in the same week**: a second save for a student/week updates the existing
  evaluation rather than creating a duplicate. When two different mentors evaluate the same
  student in the same week, the latest level per outcome wins (the change is recorded) and each
  mentor's comment is kept separately.
- **Partial evaluation**: a mentor assesses only some outcomes; the student counts as assessed
  for the week, and un-assessed outcomes simply have no level yet.
- **Week with no prior data**: pre-fill is blank for a student never evaluated before.
- **Outcome deactivated mid-program**: existing evaluations keep their levels; the outcome drops
  off new forms and the heatmap for subsequent weeks.
- **Student added mid-program**: appears as pending from the week they join; earlier weeks show
  no evaluation.
- **Week outside the program range** (before week 1 or after the last week): rejected or not
  offered.
- **Regression when the prior week was a partial evaluation**: a drop is only flagged when a
  comparable prior-week level exists for that outcome.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let a mentor record an evaluation for a given student and program week,
  assigning a level of 1, 2, 3, or 4 to one or more learning outcomes.
- **FR-002**: System MUST let a mentor attach an optional free-text comment to a student's weekly
  evaluation, and MUST attribute each evaluation (and comment) to the mentor who made it.
- **FR-003**: System MUST pre-fill the evaluation form with each outcome's most recent level for
  that student from a prior week (blank when none exists).
- **FR-004**: System MUST validate evaluations, rejecting any level outside 1–4 or any reference
  to an outcome that is not in the active catalog.
- **FR-005**: System MUST treat a save for an existing student/week as an update to that week's
  evaluation, not a new duplicate.
- **FR-006**: System MUST restrict recording an evaluation to mentors (STAFF/ADMIN) whose turma
  (`turma_ou_equipe`) matches the student's turma. A mentor covers a single turma in v1; no
  separate mentor–turma assignment model is introduced.
- **FR-007**: System MUST let administrators add, edit, and deactivate learning outcomes (each
  with a number, name, and description), and MUST keep deactivated outcomes out of new evaluation
  forms while preserving historical evaluations that reference them.
- **FR-008**: System MUST restrict learning-outcome catalog management to administrators.
- **FR-009**: System MUST present a per-turma, per-week dashboard showing the count of assessed
  students, the count and identity of pending students, and the number of students each mentor
  assessed that week. A student is **assessed** for the week once at least one LO level is recorded
  (a comment alone does not count as assessed); the per-mentor count tallies students for whom that
  mentor set ≥ 1 level.
- **FR-010**: System MUST present, on the dashboard, a heatmap of levels per outcome across the
  turma for the selected week.
- **FR-011**: System MUST flag regressions on the dashboard — a student whose level on an outcome
  is lower than that student's most recent comparable prior-week level for the same outcome.
- **FR-012**: System MUST export a per-turma, per-week report of each student's level per outcome
  and the week's comments, using the platform's existing CSV/Excel export mechanism, marking
  not-yet-evaluated students as pending.
- **FR-013**: System MUST derive the "current week" from a configurable program start date and
  operate over a configurable number of weeks, and MUST reject evaluations for weeks outside that
  range.
- **FR-014**: System MUST keep all evaluation data (forms, dashboard, report) visible only to
  mentors and administrators in v1; students (ALUNO) cannot view evaluation results. A
  student-facing view is out of scope for v1.
- **FR-015**: System MUST record, for each evaluation and comment, who recorded it and when, for
  auditability.

### Key Entities *(include if feature involves data)*

- **Learning Outcome**: An item in the evaluation catalog. Attributes: number, name, description,
  active flag, display order. Referenced by evaluations; may be deactivated but not erased while
  history references it.
- **Weekly Evaluation**: A student's assessment for one program week. Relates a student to a week
  and carries a level (1–4) per assessed learning outcome, one or more mentor comments, and the
  mentor attribution. One evaluation per student per week.
- **Evaluation Level**: The level (1–4) assigned to a specific learning outcome within a weekly
  evaluation; relates a weekly evaluation to a learning outcome.
- **Program Configuration**: The program's start date (defining week 1) and number of weeks, from
  which the current week is derived.
- **Mentor / Student** (existing `User`): Student = `ALUNO`; Mentor = `STAFF`/`ADMIN`. Reused from
  the platform; turma membership via the existing `turma_ou_equipe` field (single turma per user).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A mentor can complete and save a student's weekly evaluation in under 2 minutes with
  the form pre-filled from prior levels.
- **SC-002**: 100% of saved evaluations are retrievable for the correct student and week and are
  attributed to the mentor who recorded them.
- **SC-003**: The dashboard correctly classifies every student in a turma as assessed or pending
  for the selected week (0 misclassifications against the underlying data).
- **SC-004**: Every regression (a lower level than the student's most recent comparable prior
  week for the same outcome) is flagged, with no false regressions from non-comparable weeks.
- **SC-005**: The weekly export lists 100% of the turma's students for the week, with levels for
  the assessed and a pending marker for the rest.
- **SC-006**: Deactivating a learning outcome removes it from new evaluation forms while 100% of
  historical evaluations referencing it remain intact and exportable.

## Assumptions

- This feature is additive to lablivre-ponto-digital and reuses the existing `User` model and the
  locked technology stack (FastAPI, async SQLAlchemy/PostgreSQL, React); no new frameworks.
- Levels use a fixed 1–4 scale (1=Iniciante, 2=Básico, 3=Intermediário, 4=Avançado), matching the
  reference program.
- The LO catalog is shared across turmas (one catalog), unless later specified otherwise.
- Evaluation is weekly; a "week" is an integer index derived from the configured program start
  date, not a calendar date range the user picks per evaluation.
- A mentor may assess a subset of outcomes in a given week; the student is considered "assessed"
  for the week once at least one LO level is recorded (a comment alone does not count).
- Turma membership is stable for the program's duration in v1 (students do not change turma
  mid-program), so the evaluation's turma and the student's current turma are always equal; the
  dashboard and report use the student's turma without snapshot/live divergence.
- AI-generated summaries and PDF generation (present in the reference system) are out of scope for
  v1; the dashboard and the existing CSV/Excel export cover the reporting need.
- Authentication and roles reuse the existing platform; mentors are STAFF/ADMIN and students are
  ALUNO.
