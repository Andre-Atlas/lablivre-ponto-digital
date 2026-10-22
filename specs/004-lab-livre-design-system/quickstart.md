# Quickstart: Lab Livre Design System

## Prerequisites
- Node 20+, from `web_admin/`: `npm install` (pulls new self-hosted font + a11y deps).

## Run
```bash
cd web_admin
npm run dev          # Vite dev server
```
Open the app and the styleguide:
- App: `http://localhost:5173/`
- Styleguide (dev showcase of all components/states): `http://localhost:5173/styleguide`

## Validation scenarios

### 1. Tokens applied everywhere (SC-001, SC-002)
- Visit Login → Check-in (as ALUNO) → Dashboard + every panel (as STAFF/ADMIN).
- Confirm: Lab Livre purple header, lavender background, Poppins headings, Inter body, consistent buttons/cards/inputs/badges/tables.
- Grep guard: `rg -n "#[0-9A-Fa-f]{3,6}" web_admin/src --glob '!index.css'` returns no color literals in markup; `rg -n "dark:" web_admin/src` returns nothing.

### 2. No external font/CDN request (SC-005)
- DevTools → Network → reload. No request to `fonts.googleapis.com`/`fonts.gstatic.com` or any non-origin host. Fonts load from app origin.

### 3. Accessibility (SC-003, SC-007)
```bash
npx playwright test tests/design-system.spec.ts
```
- axe reports zero contrast/role violations on Login, Dashboard, and a panel.
- Keyboard: Tab through a form, open/close a Modal (focus trapped + restored), operate Tabs with arrow keys, dismiss a Toast — all with visible focus.

### 4. Responsive (SC-004)
- Set viewport 375px. Every screen reflows with no horizontal scrollbar; all actions reachable.

### 5. Reduced motion (FR-015)
- OS "reduce motion" on → reload Login: blobs/hero are static.

### 6. No behavior regression (SC-008)
- E2E covers: login, check-in, register student, register certificate, record LO evaluation, view attendance table, export, view LO dashboard — all pass unchanged.

## Done signal
All six scenarios pass; styleguide renders every component variant/state; CHANGELOG/README/ARCHITECTURE updated.
