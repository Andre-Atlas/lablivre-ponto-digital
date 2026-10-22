# Phase 0 Research: Lab Livre Design System

## 1. Brand extraction from the reference ("Design V3.svg")

**Method**: The 75 MB SVG embeds 9 raster images and outlines all text to vector paths (no selectable text, no `font-family`). Decision: strip the `<defs>` image block and render the vector layer with `rsvg-convert` to inspect layout; mine `fill`/`stroke`/`rx`/`stroke-width` attributes for exact tokens.

### Decision — Color palette (by on-canvas frequency)
| Token | Hex | Role (observed in reference) |
|-------|-----|------------------------------|
| primary | `#7023E8` | Header bar, headings, primary buttons (602 uses) |
| primary-dark | `#3D009C` | Deep purple accent |
| primary-light | `#AB7BF6` | Purple tint, decorative rings |
| accent (orange) | `#F46B2F` | Secondary CTA button, QORA mark, emphasis |
| accent-pink | `#E52E70` | Decorative accents |
| ink (navy) | `#080056` | Body text, borders/strokes (342 stroke uses), large blob |
| surface-lavender | `#F6F1FF` | Page background (1295 uses) |
| surface-peach | `#FFE7E1` | Co-brand band, highlighted sections |
| success | `#5AB535` | Green CTA band, success |
| danger | `#B80909` | Error |
| neutral ramp | `#303030 #333333 #444444 #707070 #C6C6C6` | Text / muted / borders |

**Rationale**: Frequencies confirm purple is primary, lavender is the base surface, navy is the text/outline color, orange is the single strong CTA accent. **Alternatives considered**: treating orange as primary (rejected — it's used only for secondary CTAs and the QORA partner mark).

### Decision — Shape language
From `rx` frequencies: pill/full radius (`rx≈26.5`, `rx≈45`+) for tags/buttons-as-pills, `rx=12` and `rx=8` for cards/inputs, small `rx=3.5/4` for chips. Strokes are thin (`0.3` hairlines at export scale) up to `2`/`4` for emphasis. **Tokens**: `radius-sm 6px`, `radius 8px` (buttons/inputs), `radius-lg 12px` (cards), `radius-full 9999px` (pills/badges).

### Decision — Layout & brand motifs
Rendered mockups show: peach co-brand strip ("MAIS UM PROJETO POR" + QORA) → purple nav header with white "Lab Livre" wordmark (leaf/heart glyph) + nav + Instagram/GitLab icons → hero with large faded "typewriter" display text + big organic navy blob → stat callouts ("1500+ Estudantes Formados") → lavender cards → green full-width CTA band → deep-navy footer. Decorative purple rings, green and orange blobs scattered. **Rationale**: these motifs define "expressive on entry"; the data screens in our app will use the restrained subset (header, cards, buttons, tables) only.

## 2. Typography

**Decision**: Poppins (display/headings) + Inter (body/UI), self-hosted via `@fontsource/poppins` and `@fontsource/inter`, imported in `index.css`, with `font-display: swap` (the `@fontsource` default). **Rationale**: the reference display face is a bold, friendly geometric sans with double-story `a` and rounded terminals — Poppins is the closest widely-available open-source match; Inter is a neutral humanist UI face ideal for dense tables/forms. User confirmed this pairing. Self-hosting satisfies the "no runtime CDN request" + privacy requirement. **Alternatives considered**: Montserrat (slightly more corporate), Plus Jakarta single-family (less heading/body contrast) — both rejected by the user in favor of Poppins + Inter. Loading via Google Fonts `<link>` rejected (external request).

**Type scale** (see data-model.md for exact values): display, h1, h2, h3, h4, body-lg, body, small, overline (uppercase, letter-spaced, navy).

## 3. Tailwind v4 token strategy

**Decision**: Define every token inside the existing `@theme { … }` block in `src/index.css` (colors as `--color-*`, fonts as `--font-*`, radius as `--radius-*`, plus custom `--space-*`, `--shadow-*`, `--duration-*`). Tailwind v4 auto-generates utilities (`bg-primary`, `text-ink`, `rounded-card`, `font-display`, etc.). A `@layer base` sets html/body defaults (lavender bg, Inter body, navy ink). **Rationale**: this is the stack's current, config-less idiom (no `tailwind.config.js`); keeps one source of truth; satisfies "no hard-coded colors in markup". **Alternatives considered**: a separate design-tokens JSON + build step (rejected — adds tooling the stack doesn't have, violates Stack Stability spirit); inline CSS variables without Tailwind (rejected — loses utility ergonomics the codebase relies on).

## 4. Dark mode removal

**Decision**: Remove `@custom-variant dark`, all `dark:` utilities, `ThemeToggle.tsx`, and `isDark/toggleTheme` from `App.tsx`; stop writing `theme`/`.dark` to `localStorage`/`documentElement`. **Rationale**: user chose light-only; the reference has no dark brand. Recorded as a Constitution VI deviation. **Risk/mitigation**: ensure no component relies on `.dark` for correct contrast in light mode (grep for `dark:` and remove each deliberately).

## 5. Accessibility & motion

**Decision**: Enforce WCAG AA via token pairing rules (navy/ink text on lavender/white; white text on purple/orange passes AA at the shown sizes — verify orange `#F46B2F` as a *background for white text* at ≥18px/bold only, otherwise use it for large CTA labels; for small text on orange use navy). Visible `focus-visible` ring using primary. Respect `prefers-reduced-motion` to disable blob/typewriter animation. **Rationale**: AA is a hard requirement (FR-013) and the orange accent is the one combo needing care. **Alternatives considered**: darkening orange globally (rejected — changes brand fidelity; instead constrain its use as a text background).

## 6. Component architecture

**Decision**: Presentational, prop-driven React components in `src/components/ui/`, TypeScript-typed, forwarding refs where native (Button/Input), composing native elements for semantics (`<dialog>`-like Modal with focus trap, `role="tablist"` Tabs, `aria-live` Toast). No new state-management library — local state + existing patterns. **Rationale**: keeps bundle small, aligns with Stack Stability; contracts in `contracts/components.md`. **Alternatives considered**: adopting Radix/Headless UI (rejected — new dependency; the component set is small enough to build natively and keeps the stack locked).

## Open questions

None. All four brand decisions resolved with the user prior to spec authoring.
