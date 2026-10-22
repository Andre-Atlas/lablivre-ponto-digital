# Phase 1 Contracts: Component Library API

Prop/behavior contracts for `web_admin/src/components/ui/`. Each component is presentational, TypeScript-typed, token-only, and ships every applicable state from data-model.md. Props listed are the public contract; components may accept standard HTML attrs via `...rest`.

## Button
`variant: "primary" | "secondary" | "ghost" | "danger"` (default `primary`) · `size: "sm" | "md" | "lg"` (default `md`) · `loading?: boolean` · `disabled?: boolean` · `iconLeft?/iconRight?: ReactNode` · `as?: "button" | "a"` · forwards ref.
- primary = purple fill/white; secondary = orange fill/white; ghost = transparent/purple text + border; danger = red.
- Radius `--radius`; focus-visible ring; loading shows spinner + `aria-busy`, disables click.

## Card
`as?` · `padding?: "sm"|"md"|"lg"` · `interactive?: boolean` (hover elevation) · children. White surface, `--radius-lg`, `--shadow`. Subcomponents: `Card.Header`, `Card.Body`, `Card.Footer`.

## Input / Textarea
`label: string` (required for a11y) · `error?: string` · `hint?: string` · `id?` (auto-generated if absent) · native props. Renders `<label htmlFor>`; on error sets `aria-invalid` + `aria-describedby` to the message; border uses `--color-border` → `danger` on error; focus ring primary.

## Select
Same label/error/hint contract as Input, wraps native `<select>` for built-in keyboard/a11y. `options: {value,label}[]` or children `<option>`.

## Badge (pill)
`tone: "neutral"|"primary"|"success"|"danger"|"accent"` · `size?: "sm"|"md"`. `--radius-full`, tonal bg + readable text (AA). Used for statuses (PRESENTE/FALTA/JUSTIFICADO, LO levels).

## Table
`columns: {key,header,align?,width?}[]` · `data: Row[]` · `renderCell?` · `empty?: ReactNode` · `stickyHeader?: boolean`. Semantic `<table>`/`<thead>`/`<tbody>`; header navy text on peach/lavender; zebra via surface; horizontal scroll container (no page overflow); `empty` → EmptyState when no rows.

## Modal / Dialog
`open: boolean` · `onClose: () => void` · `title: string` · `size?` · children · `footer?`. Behavior: `role="dialog"` + `aria-modal`, `aria-labelledby` title; focus trapped inside; focus restored to trigger on close; `Esc` and backdrop click close; background inert; `--shadow-lg`, `--radius-lg`.

## Tabs
`tabs: {id,label,content}[]` · `defaultTab?` · controlled `value?/onChange?`. `role="tablist"/"tab"/"tabpanel"`, arrow-key navigation, `aria-selected`, roving tabindex. Active tab underline/fill in primary.

## Toast / Alert
Inline `Alert`: `tone: "info"|"success"|"warning"|"danger"` · `title?` · children · `onDismiss?`. Toast system: `useToast()` + `<ToastProvider>`; toasts in an `aria-live="polite"` region, auto-dismiss (pausable), stacked top-right, reduced-motion aware.

## PageHeader
`title: string` · `eyebrow?: string` (overline) · `description?` · `actions?: ReactNode` · `blob?: boolean` (entry surfaces). h1 in display/primary; eyebrow overline; actions right-aligned, wrap on mobile.

## StatCallout
`value: string|number` · `label: string` · `tone?`. Large display value (e.g. "1500+") + overline label, as seen in the reference.

## Blob
`variant: "navy"|"purple-ring"|"green"|"orange"` · `size` · `className` for positioning. Decorative SVG, `aria-hidden`, pointer-events none; optional slow drift animation disabled under reduced-motion.

## EmptyState
`icon?/blob?` · `title: string` · `description?` · `action?: ReactNode`. On-brand empty presentation for zero-row tables/lists.

## Shared chrome (not in `ui/` but part of the system)
- **AppHeader**: purple bar, LabLivreLogo, nav/actions slot, user menu/logout. Used by Dashboard/Checkin.
- **AppFooter**: navy footer with brand + links.
- **LabLivreLogo**: `variant: "light"|"dark"`, standardized glyph + wordmark.

## Non-functional contract (all components)
- Only design tokens for color/space/radius/shadow/motion — no literal hex.
- Keyboard operable; `focus-visible` indicator present.
- Responsive from 375px; no fixed widths that overflow.
- Reduced-motion respected.
