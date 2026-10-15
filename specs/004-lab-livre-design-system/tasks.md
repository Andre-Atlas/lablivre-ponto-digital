---
description: "Task list for Lab Livre Design System"
---

# Tasks: Lab Livre Design System

**Input**: Design documents from `/specs/004-lab-livre-design-system/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/components.md, quickstart.md
**Tests**: E2E + a11y are REQUIRED by the spec (SC-003/007/008) and constitution (Principle V) → included.

**All paths are under `web_admin/` unless noted.**

## Format: `[ID] [P?] [Story] Description`
- **[P]**: parallelizable (different files, no incomplete-dep)
- **[Story]**: US1 (consistent on-brand), US2 (component library), US3 (a11y/responsive)

---

## Phase 1: Setup

- [x] T001 Add self-hosted font + a11y dev deps in `web_admin/package.json`: `@fontsource/poppins`, `@fontsource/inter`, `@axe-core/playwright`; run `npm install`.
- [x] T002 Remove dead/legacy frontend scripts & assets that encode the old brand: delete unused root helper scripts (`web_admin/*.cjs`, `screenshot*.js`, `remove_bg*.py`, `trace_logo.cjs`, `logo_traced.svg`, `current_logo.png`) only if not referenced by build/tests; keep `playwright.config.ts`, `vite.config.ts`, `index.html`. (Audit with `rg` before deleting.)
- [x] T003 [P] Create `web_admin/src/components/ui/` directory and empty `index.ts` barrel.

## Phase 2: Foundational (BLOCKS all user stories)

**Token layer + fonts + base — nothing visual is on-brand until this lands.**

- [x] T004 Rewrite `web_admin/src/index.css` `@theme` with the full token catalog from data-model.md: colors (primary/primary-dark/primary-light/accent/accent-pink/ink/success/danger/bg/peach/surface + neutral ramp), `--font-display`/`--font-body`, `--radius-*`, `--shadow-*`, `--duration-*`/`--ease`. Remove old `--color-magenta/cyan/orange`.
- [x] T005 In `web_admin/src/index.css`, import self-hosted fonts (`@fontsource/poppins` weights 400/600/700, `@fontsource/inter` 400/500/600) and add `@layer base`: html/body use `--color-bg` + `--font-body` + `--color-ink`; headings default `--font-display`; `*:focus-visible` ring token; global `@media (prefers-reduced-motion: reduce)` reset.
- [x] T006 Remove dark mode globally: delete `@custom-variant dark` from `index.css`; delete `web_admin/src/components/ThemeToggle.tsx`; remove `isDark/toggleTheme/localStorage theme/.dark` logic from `web_admin/src/App.tsx` (preserve auth + ALUNO-vs-STAFF/ADMIN routing exactly); update `index.html` if it bootstraps a theme class.
- [x] T007 [P] Add typography helper classes/utilities for the type scale (display, h1–h4, body-lg, body, small, overline) in `index.css` `@layer components` (or document the token utilities to use), per data-model.md scale.
- [x] T008 [P] Standardize `web_admin/src/components/LabLivreLogo.tsx` to the brand (leaf/heart glyph + wordmark, `variant: "light"|"dark"`); remove `web_admin/src/components/EldoradoLogo.tsx` and its imports.

**Checkpoint**: App compiles, loads in light theme with lavender bg + brand fonts; no dark toggle; no old palette tokens.

---

## Phase 3: User Story 2 — Reusable component library (Priority: P2)

**Built before US1 restyle because US1 screens consume these. Independently testable via the styleguide route.**

- [x] T009 [P] [US2] `ui/Button.tsx` — variants primary/secondary/ghost/danger, sizes sm/md/lg, loading/disabled/icon props, focus ring (contracts/components.md).
- [x] T010 [P] [US2] `ui/Card.tsx` — Card + Card.Header/Body/Footer, padding + interactive props.
- [x] T011 [P] [US2] `ui/Input.tsx` and `ui/Textarea.tsx` — label/error/hint, `aria-invalid`/`aria-describedby`, auto id.
- [x] T012 [P] [US2] `ui/Select.tsx` — native select wrapper, label/error/hint, options prop.
- [x] T013 [P] [US2] `ui/Badge.tsx` — pill, tones neutral/primary/success/danger/accent, sizes.
- [x] T014 [P] [US2] `ui/Table.tsx` — semantic table, columns/data/renderCell, sticky header, horizontal-scroll container, empty slot.
- [x] T015 [P] [US2] `ui/Modal.tsx` — dialog role + aria-modal, focus trap + restore, Esc/backdrop close, sizes.
- [x] T016 [P] [US2] `ui/Tabs.tsx` — tablist/tab/tabpanel roles, arrow-key roving tabindex, controlled+uncontrolled.
- [x] T017 [P] [US2] `ui/Toast.tsx` — ToastProvider + useToast, `aria-live` region, auto-dismiss (pausable), stacking; plus inline `Alert`.
- [x] T018 [P] [US2] `ui/PageHeader.tsx` + `ui/StatCallout.tsx` — eyebrow/title/description/actions; large value + overline label.
- [x] T019 [P] [US2] `ui/Blob.tsx` + `ui/EmptyState.tsx` — decorative aria-hidden brand shapes (reduced-motion static); on-brand empty presentation.
- [x] T020 [US2] Export all components from `ui/index.ts`; add `web_admin/src/styleguide/Styleguide.tsx` rendering every component in all variants/states; wire a dev route `/styleguide` (react-router) gated to dev or always-available internal route.
- [x] T021 [US2] Shared chrome: `components/AppHeader.tsx` (purple bar, logo, nav/actions, logout) and `components/AppFooter.tsx` (navy footer) from the reference, token-only.

**Checkpoint (US2 done)**: `/styleguide` shows the full library; every component uses tokens, is keyboard-operable, has all states.

---

## Phase 4: User Story 1 — Consistent on-brand experience, every screen (Priority: P1) 🎯 MVP

**Re-skin each screen using the library. Behavior/data flows unchanged.**

- [x] T022 [US1] Re-skin `web_admin/src/pages/Login.tsx` — expressive entry: peach co-brand strip, purple header, hero with brand display type + Blob, Lab Livre logo, Button/Input from library; preserve auth submit + error handling + onLogin flow.
- [x] T023 [US1] Re-skin `web_admin/src/pages/Checkin.tsx` (student) — expressive but focused: AppHeader, brand hero/StatCallout, QR (`qrcode.react`) in a Card, Button; preserve check-in logic + turno handling + logout.
- [x] T024 [US1] Re-skin `web_admin/src/pages/Dashboard.tsx` — calm/data: AppHeader + AppFooter, PageHeader, Tabs/Cards for sections, Table for attendance, Modal for register-student, Badge for statuses, Buttons for actions/export; preserve ALL existing handlers, state, API calls, panel toggles, and the register-aluno modal behavior.
- [x] T025 [P] [US1] Re-skin `web_admin/src/components/CertificadosPanel.tsx` — Card/Table/Modal/Input/Badge; preserve upload (`multipart`) + list + justify-day behavior.
- [x] T026 [P] [US1] Re-skin `web_admin/src/components/AvaliacoesPanel.tsx` — form via library Inputs/Select/Textarea, Badge for LO levels, Button; preserve evaluation upsert + week selection.
- [x] T027 [P] [US1] Re-skin `web_admin/src/components/LOCatalogPanel.tsx` — Table/Card/Badge; preserve catalog list/filter behavior.
- [x] T028 [P] [US1] Re-skin `web_admin/src/components/LODashboardPanel.tsx` — StatCallout/Card/Table/Badge for the LO-evolution dashboard; preserve data fetch + aggregation display; on-brand empty/loading states.
- [x] T029 [US1] Sweep for consistency: replace any remaining ad-hoc colors/spacing in screens with tokens; ensure loading/empty/error states on every async surface use library components.

**Checkpoint (US1 done = MVP)**: every screen on-brand, old palette gone, dark styling gone, behavior intact.

---

## Phase 5: User Story 3 — Accessible & responsive by default (Priority: P3)

- [x] T030 [US3] Responsive pass: verify/fix 375px→desktop reflow on Login, Checkin, Dashboard, all panels; no horizontal overflow; actions reachable; AppHeader nav collapses gracefully.
- [x] T031 [US3] Accessibility pass: run axe on key screens, fix contrast/roles/labels; verify focus order, modal focus trap/restore, tabs keyboard nav, toast live-region, reduced-motion static blobs.

## Phase 6: Polish & Cross-cutting

- [x] T032 [P] Write `web_admin/tests/design-system.spec.ts` (Playwright): (a) axe zero-violations on Login/Dashboard/a panel; (b) keyboard operation of Modal + Tabs + Toast; (c) 375px no-overflow; (d) no external font/CDN network request; (e) smoke of each preserved flow (login, check-in, register student, certificate, LO eval, attendance view, export).
- [x] T033 [P] Guard checks: `rg "#[0-9A-Fa-f]{3,6}" web_admin/src --glob '!*index.css'` → no color literals in markup; `rg "dark:" web_admin/src` → empty; `rg "EldoradoLogo|ThemeToggle|isDark" web_admin/src` → empty.
- [x] T034 Build + lint: `npm run build` (tsc + vite) clean; `npx oxlint` clean.
- [x] T035 Living docs (Constitution VI): update `web_admin/README.md` (design system + styleguide usage, light-only note), `docs/ARCHITECTURE.md` / `ARCHITECTURE.md` (frontend design-system section + removed dark mode), and `CHANGELOG.md` (the refactor + token/brand change).
- [x] T036 Final visual verification: run the app, screenshot Login + Dashboard + one panel, compare against the Lab Livre reference motifs; confirm quickstart.md scenarios 1–6 pass.

---

## Dependencies & order
- **Setup (T001–T003)** → **Foundational (T004–T008)** blocks everything.
- **US2 (T009–T021)** before **US1 (T022–T029)** (screens consume components).
- **US3 (T030–T031)** after US1 screens exist.
- **Polish (T032–T036)** last.
- `[P]` tasks within a phase touch different files and can run together.

## Parallel opportunities
- T009–T019 (component files) all `[P]` — the bulk of US2 in parallel.
- T025–T028 (panels) all `[P]` — independent files.
- T032–T033 `[P]`.

## MVP scope
**US1 (via Foundational + US2)** = the MVP: tokens + component library + every screen visibly on-brand with behavior preserved. US3 + Polish harden and verify.
