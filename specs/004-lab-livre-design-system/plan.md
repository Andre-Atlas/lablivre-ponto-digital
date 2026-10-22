# Implementation Plan: Lab Livre Design System

**Branch**: `004-lab-livre-design-system` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-lab-livre-design-system/spec.md`

## Summary

Establish a single Lab Livre design system for the `web_admin` frontend — design tokens (color, type, spacing, radius, elevation, motion), self-hosted Poppins + Inter fonts, and a reusable component library — then re-skin every existing screen on top of it. Light mode only; dark mode removed. Branding is "expressive on entry, calm on data". No backend/API/behavior changes.

Technical approach: express all tokens through Tailwind v4's CSS-first `@theme` block in `src/index.css` (the stack's existing styling mechanism), build a small set of presentational React components under `src/components/ui/` that consume only those tokens, self-host fonts via `@fontsource` packages (additive, within the existing Vite/React layer), and migrate each screen to the new components. Validate with Playwright E2E (behavior preserved) plus automated accessibility (axe) and viewport checks.

## Technical Context

**Language/Version**: TypeScript ~5.x on React 19

**Primary Dependencies**: React 19, Vite 8, Tailwind CSS v4 (`@tailwindcss/vite`, CSS-first `@theme`), lucide-react (icons), react-router-dom 7, axios. **New (additive, justified below)**: `@fontsource/poppins` + `@fontsource/inter` (self-hosted fonts); `@axe-core/playwright` (a11y assertions in existing Playwright suite).

**Storage**: N/A (frontend-only; no persistence change)

**Testing**: Playwright (E2E, already configured) + `@axe-core/playwright` for accessibility; visual review via the styleguide route.

**Target Platform**: Modern browsers; responsive ~375px → desktop.

**Project Type**: Web application — frontend (`web_admin/`) only in scope.

**Performance Goals**: No render regressions; fonts self-hosted with `swap` (no FOIT, no runtime CDN request); first meaningful paint not degraded by the token refactor.

**Constraints**: No external font/CDN requests at runtime; WCAG AA contrast; reduced-motion honored; no hard-coded colors outside token definitions; all existing behavior/routes/copy preserved.

**Scale/Scope**: 1 token layer + ~13 UI components + 1 styleguide route; 7 screens re-skinned (Login, Checkin, Dashboard, CertificadosPanel, AvaliacoesPanel, LOCatalogPanel, LODashboardPanel) + shared header/footer/logo.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Stack Stability | ✅ PASS | No framework/language/DB change. Only additive, actively-maintained libraries that stay within the existing React/Vite/Playwright layer (`@fontsource/*` for self-hosting the chosen fonts; `@axe-core/playwright` for the existing E2E suite). They add capability, don't replace any. |
| II. Contract-First & Decoupled | ✅ PASS | No API contract changes. Component prop APIs ("UI contracts") are defined in `contracts/` before implementation. Frontend stays decoupled; still talks to `/api/v1/*` unchanged. |
| III. Async & Stateless | ✅ PASS | Frontend-only; no server state introduced. |
| IV. Security & RBAC | ✅ PASS | No auth/role/validation change. Role-based screen routing (ALUNO vs STAFF/ADMIN) preserved exactly. |
| V. Test-First Quality Gates | ✅ PASS | Playwright E2E asserts behavior is unchanged per screen; axe asserts a11y; viewport checks assert responsiveness. Backend coverage untouched (no backend change). |
| VI. Impeccable UX & Living Docs | ⚠️ DEVIATION (justified) | UX states (loading/empty/error/focus/labels) are *strengthened*. BUT this principle requires "automatic Light/Dark themes"; this feature intentionally ships **light only**. Recorded in Complexity Tracking. Living docs (README, ARCHITECTURE, CHANGELOG) updated in-change. |

**Gate result**: PASS with one documented deviation (light-only theme, user-approved). Proceed.

## Project Structure

### Documentation (this feature)

```text
specs/004-lab-livre-design-system/
├── plan.md              # This file
├── research.md          # Phase 0 output — token extraction + tech decisions
├── data-model.md        # Phase 1 output — the token catalog (design-system "data model")
├── quickstart.md        # Phase 1 output — how to run/verify the system
├── contracts/           # Phase 1 output — component prop/behavior contracts
│   └── components.md
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
web_admin/
├── index.html                      # <html lang>, no dark class bootstrap
├── src/
│   ├── index.css                   # @theme tokens (colors, fonts, radius, spacing, shadow, motion) + base layer + font imports
│   ├── main.tsx
│   ├── App.tsx                     # remove isDark/toggleTheme; role routing preserved
│   ├── styleguide/
│   │   └── Styleguide.tsx          # living component showcase (dev route)
│   ├── components/
│   │   ├── ui/                     # NEW — the design-system component library
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Textarea.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   ├── StatCallout.tsx
│   │   │   ├── Blob.tsx             # decorative brand shapes
│   │   │   ├── EmptyState.tsx
│   │   │   └── index.ts            # barrel export
│   │   ├── LabLivreLogo.tsx         # standardized to brand
│   │   ├── AppHeader.tsx            # NEW — shared purple header + nav
│   │   ├── AppFooter.tsx            # NEW — shared navy footer
│   │   ├── CertificadosPanel.tsx    # re-skinned
│   │   ├── AvaliacoesPanel.tsx      # re-skinned
│   │   ├── LOCatalogPanel.tsx       # re-skinned
│   │   └── LODashboardPanel.tsx     # re-skinned
│   │   # ThemeToggle.tsx + EldoradoLogo.tsx REMOVED
│   └── pages/
│       ├── Login.tsx               # re-skinned (expressive)
│       ├── Checkin.tsx             # re-skinned (expressive)
│       └── Dashboard.tsx           # re-skinned (calm/data)
└── tests/                          # Playwright specs: behavior + a11y + responsive
    └── design-system.spec.ts        # NEW
```

**Structure Decision**: Single web frontend (`web_admin/`). Tokens live in `src/index.css` `@theme` (the Tailwind v4 idiom already in use). A new `src/components/ui/` holds the component library; a dev-only `src/styleguide/` route showcases it. Existing `pages/` and feature `components/` are migrated in place. `ThemeToggle.tsx` and the unused `EldoradoLogo.tsx` are removed as part of the light-only + single-brand consolidation.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Light-only theme (deviates from Constitution VI "automatic Light/Dark themes") | The authoritative brand reference ("Design V3") is defined in light only; the user explicitly chose to ship a single light theme to match the brand and reduce surface area. Maintaining a brand-faithful dark palette that nobody specified would be speculative work. | Keeping dark mode was rejected because there is no dark brand reference to be faithful to, and the user directed its removal. If a dark brand is defined later, it returns via a constitution-compliant follow-up feature. |
| Additive deps `@fontsource/*`, `@axe-core/playwright` | Self-hosting the chosen brand fonts (no runtime CDN) and asserting accessibility in the existing E2E suite. | Linking Google Fonts via CDN was rejected (violates the no-external-request requirement + privacy). Hand-rolling a11y assertions was rejected as reinventing a maintained tool. |
