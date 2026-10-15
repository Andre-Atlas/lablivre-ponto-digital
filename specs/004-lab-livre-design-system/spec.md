# Feature Specification: Lab Livre Design System

**Feature Branch**: `004-lab-livre-design-system`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Create a platform-wide Lab Livre design system for the web_admin frontend based on the Design V3 reference, and apply it across the entire app, following design and front-end good practices, via spec-kit."

## Overview

The `web_admin` frontend currently mixes an ad-hoc palette (magenta/cyan/orange) with inconsistent, one-off component styling across screens. This feature establishes a single, cohesive **Lab Livre design system** — a documented set of design tokens (color, typography, spacing, radius, elevation, motion), a reusable component library, and brand assets — derived from the official Lab Livre institutional brand reference ("Design V3"). It then re-skins every existing screen on top of that system so the whole product looks and behaves like one deliberately-designed Lab Livre product.

This is a **visual and front-end refactor only**. No backend endpoints, data flows, routes, or product features change. Every screen keeps its current behavior; only its presentation and the components it is built from change.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consistent, on-brand experience across every screen (Priority: P1)

As any user of the platform (student, professor/staff, or admin), when I move between the login screen, my working screen, and any panel, every screen uses the same Lab Livre colors, typography, spacing, and components, so the product feels like one coherent, professional, trustworthy tool rather than a patchwork.

**Why this priority**: This is the core deliverable and the reason for the work. Without a consistently applied system, nothing else matters. It is the MVP: tokens defined + every screen visibly on-brand.

**Independent Test**: Log in and visit every screen (Login, student Check-in, Dashboard, and each admin panel). Confirm all use the Lab Livre purple/orange/navy palette, Poppins headings + Inter body, consistent button/card/input styling, and no remnants of the old magenta/cyan palette or dark-mode styling.

**Acceptance Scenarios**:

1. **Given** a visitor on the login screen, **When** the page loads, **Then** it shows Lab Livre branding (logo, purple header treatment, brand typography) and brand-consistent, expressive entry styling (hero/decorative elements) without external font/CDN network requests.
2. **Given** an authenticated user navigating between any two screens, **When** they compare the two, **Then** primary buttons, secondary buttons, cards, inputs, badges, tables, and modals are visually identical in style across both.
3. **Given** any screen in the app, **When** it is inspected, **Then** no color value is hard-coded outside the design tokens and no old-palette or dark-mode artifact remains.

---

### User Story 2 - Reusable component library for all current and future screens (Priority: P2)

As a developer extending the platform, I can build any screen from a documented set of shared UI components (buttons, cards, inputs, selects, textareas, badges/pills, tables, modals, tabs, toasts/alerts, page headers, stat callouts, decorative blobs), so I never re-invent styling and the product stays consistent as it grows.

**Why this priority**: The component library is what makes consistency sustainable. It can be delivered and demonstrated (e.g., a living styleguide page) independently of restyling every screen.

**Independent Test**: Open the styleguide/showcase and confirm every component renders in all its documented variants and states (default, hover, focus, active, disabled, error, loading, empty) using only design tokens.

**Acceptance Scenarios**:

1. **Given** the component library, **When** a developer uses the Button component, **Then** primary (purple), secondary (orange), and ghost/subtle variants are available with consistent sizing, radius, focus ring, and disabled treatment.
2. **Given** any interactive component (modal, tabs, toast, menu), **When** operated by keyboard only, **Then** focus is visible, focus order is logical, and the expected ARIA roles/attributes are present.
3. **Given** a form built from library inputs, **When** a field has an error, **Then** the error state is shown consistently (color token, message, and accessible association) across every form in the app.

---

### User Story 3 - Accessible and responsive by default (Priority: P3)

As a user on any device or with accessibility needs, every screen is legible, operable by keyboard, respects reduced-motion preferences, and reflows cleanly from mobile to desktop, so the brand refresh does not cost usability.

**Why this priority**: Good-practice requirements that harden the system; valuable but build on top of the tokens and components from US1/US2.

**Independent Test**: Run an accessibility audit and responsive check across the main screens; confirm AA contrast, keyboard operability, reduced-motion behavior, and no horizontal overflow at mobile widths.

**Acceptance Scenarios**:

1. **Given** any text or interactive element, **When** its colors are measured against the design tokens, **Then** contrast meets WCAG AA (4.5:1 body text, 3:1 large text and UI boundaries).
2. **Given** a user with "reduce motion" enabled, **When** a screen with decorative/hero animation loads, **Then** motion is disabled or minimized.
3. **Given** any screen at a 375px-wide viewport, **When** it renders, **Then** content reflows without horizontal scrolling and all actions remain reachable.

---

### Edge Cases

- **Long content**: Headings, badges, and table cells with very long text (long student names, long LO descriptions) must truncate or wrap predictably without breaking layout.
- **Empty states**: Lists/tables with zero rows show an on-brand empty state (illustration/blob + message), not a blank area.
- **Loading & error states**: Async panels show consistent loading and error presentations drawn from the system, not ad-hoc spinners/messages.
- **Dense data**: Attendance and evaluation tables with many rows/columns remain legible under the "calm on data" styling (no decorative clutter interfering with scanning).
- **Focus trapping**: Opening a modal moves focus into it and restores focus to the trigger on close.
- **Reduced motion**: Decorative blobs and hero/typewriter effects must have a static fallback.

## Requirements *(mandatory)*

### Functional Requirements

**Design tokens**

- **FR-001**: The system MUST define the Lab Livre color palette as named design tokens: primary purple `#7023E8` (+ dark `#3D009C`, light `#AB7BF6`), accent orange `#F46B2F`, accent pink `#E52E70`, deep navy `#080056`, surfaces lavender `#F6F1FF` and peach `#FFE7E1` and white, semantic success `#5AB535` and danger `#B80909`, and a neutral text/border ramp (`#303030`/`#333333`/`#444444`/`#707070`/`#C6C6C6`).
- **FR-002**: The system MUST define typography tokens using Poppins for display/headings and Inter for body/UI, with a documented type scale (display, h1–h4, body, small, overline/eyebrow uppercase labels), including size, weight, and line-height for each.
- **FR-003**: The system MUST define spacing, border-radius (including a full/pill radius for tags and ~8–12px for buttons/cards), elevation/shadow, and motion-duration tokens, and all screens MUST consume these rather than hard-coded values.
- **FR-004**: Fonts MUST be self-hosted (no external CDN/Google Fonts network request at runtime) and loaded with a swap strategy so text is never invisible while fonts load.

**Component library**

- **FR-005**: The system MUST provide reusable components covering at minimum: Button (primary/secondary/ghost), Card, Input, Select, Textarea, Badge/Tag (pill), Table, Modal/Dialog, Tabs, Toast/Alert, PageHeader, StatCallout, and a decorative Blob/brand-shape element.
- **FR-006**: Each interactive component MUST define and style all applicable states: default, hover, focus-visible, active, disabled, error, loading, and empty.
- **FR-007**: Interactive components MUST use semantic HTML and appropriate ARIA roles/attributes (e.g., dialog semantics + focus trap for Modal, tab semantics for Tabs, live-region for Toast), and be fully operable by keyboard with a visible focus indicator.
- **FR-008**: The system SHOULD provide a living styleguide/showcase surface that renders every component and its variants/states for review and regression.

**Brand application**

- **FR-009**: The system MUST apply "expressive on entry, calm on data" branding: Login, student Check-in, and empty states MAY use expressive brand elements (decorative blobs, large brand headings, QORA co-brand treatment); data-dense admin screens (attendance tables, forms, panels) MUST stay visually restrained to preserve legibility.
- **FR-010**: The Lab Livre logo, header, and footer MUST be standardized to the brand reference and used consistently across the app.
- **FR-011**: Every existing screen MUST be migrated to the design system: Login, Check-in, Dashboard, and all panels (medical certificates, LO evaluations, LO catalog, LO dashboard).
- **FR-012**: The system MUST remove dark mode entirely — the theme toggle, dark state, the dark style variant, and all dark-mode utility usages — delivering a single light theme.

**Non-functional / good practice**

- **FR-013**: All color combinations used for text and essential UI MUST meet WCAG AA contrast.
- **FR-014**: Screens MUST be responsive across mobile (~375px) through desktop with no horizontal overflow and all actions reachable at every breakpoint.
- **FR-015**: Decorative/hero motion MUST respect the user's reduced-motion preference with a static fallback.
- **FR-016**: The refactor MUST preserve all existing behavior, routes, data flows, and copy; no functional regressions.

### Key Entities *(design-system artifacts, not database entities)*

- **Design Token**: A named, reusable design decision (color, font family/size/weight, spacing step, radius, shadow, motion duration) that is the single source of truth consumed by every component and screen.
- **Component**: A reusable UI building block with defined variants and states, built only from tokens.
- **Brand Asset**: Logo, co-brand mark, and decorative brand shapes (blobs) used per the "expressive on entry" rule.
- **Screen**: An existing app view (Login, Check-in, Dashboard, each panel) that is re-composed from components and tokens.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of app screens (Login, Check-in, Dashboard, and all 4 panels) use the Lab Livre tokens and components, with zero occurrences of the previous magenta/cyan palette or any dark-mode styling remaining.
- **SC-002**: 100% of color values in the frontend resolve through design tokens; no hard-coded hex colors appear in screen/component markup outside the token definitions.
- **SC-003**: All primary text and interactive elements meet WCAG AA contrast (verified by an automated accessibility check reporting zero contrast violations on the main screens).
- **SC-004**: Every screen renders without horizontal scrolling at a 375px viewport and remains usable through desktop widths.
- **SC-005**: No external font or CDN network request is made at runtime (fonts load from the app's own origin), verified in the network panel.
- **SC-006**: The component library covers 100% of the UI patterns used by the existing screens (every screen can be built without introducing new one-off styled elements).
- **SC-007**: All interactive components are fully operable by keyboard with a visible focus indicator and pass a basic screen-reader semantics check.
- **SC-008**: No functional regression — every pre-existing user flow (login, check-in, register student, register certificate, record LO evaluation, view attendance, export, view dashboards) works exactly as before.

## Assumptions

- The reference "Design V3.svg" is the authoritative brand source; its text was outlined (not selectable), so the exact typefaces are not recoverable from the file — Poppins (display) and Inter (body) were chosen by the user as the closest open-source match and are the canonical fonts for this system.
- Light mode only is intended; removing dark mode is a deliberate decision, not a regression.
- The QORA co-brand treatment from the reference applies to Lab Livre-branded entry surfaces; it is decorative and carries no new functionality.
- The target is the `web_admin` React/Tailwind frontend only. The Flet `desktop_app` and the backend are out of scope.
- "Entire app" means every currently existing screen and shared chrome (header/footer); no new product screens are added by this feature.
- Existing routing, API client, auth/session handling, and component behavior are reused unchanged; only presentation changes.

## Out of Scope

- Backend/API changes, database changes, and new product features.
- The Flet `desktop_app`.
- Internationalization/content rewrites (existing copy is preserved).
- Adding new screens or flows beyond re-skinning existing ones (a styleguide/showcase surface is a developer tool, not a product screen).
