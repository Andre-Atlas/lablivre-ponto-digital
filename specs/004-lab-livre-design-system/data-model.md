# Phase 1 Data Model: Design Token Catalog

For a design system the "data model" is the token catalog — the single source of truth consumed by every component and screen. These are expressed in `web_admin/src/index.css` inside Tailwind v4's `@theme` block.

## Color tokens

```
--color-primary:        #7023E8   /* purple — headers, headings, primary actions */
--color-primary-dark:   #3D009C   /* hover/pressed, deep accents */
--color-primary-light:  #AB7BF6   /* tints, rings, subtle fills */
--color-accent:         #F46B2F   /* orange — secondary CTA, emphasis */
--color-accent-pink:    #E52E70   /* decorative highlight */
--color-ink:            #080056   /* navy — primary text, borders, footer, blob */
--color-success:        #5AB535   /* positive state, CTA band */
--color-danger:         #B80909   /* errors, destructive */

/* Surfaces */
--color-bg:             #F6F1FF   /* lavender — app background */
--color-peach:          #FFE7E1   /* co-brand band / highlighted sections */
--color-surface:        #FFFFFF   /* cards, inputs */

/* Neutral ramp */
--color-text:           #303030   /* default body text (alt to ink for long copy) */
--color-text-strong:    #333333
--color-muted:          #707070   /* secondary text, placeholders */
--color-border:         #C6C6C6   /* hairline borders, dividers */
--color-border-strong:  #080056   /* emphasized outline (brand navy) */
```

**Pairing rules (WCAG AA)**:
- Body text: `ink`/`text` on `bg`/`surface`/`peach` → passes.
- White text: on `primary`, `primary-dark`, `ink`, `success` → passes. On `accent` (orange) only for **large/bold** labels (≥18px or 14px bold); for small text on orange use `ink`.
- `muted` is for ≥14px secondary text on light surfaces only.

## Typography tokens

```
--font-display: "Poppins", ui-sans-serif, system-ui, sans-serif;   /* headings */
--font-body:    "Inter", ui-sans-serif, system-ui, sans-serif;     /* body/UI */
```

**Type scale** (class intent → size / line-height / weight / family):
| Role | Size | Line-height | Weight | Family |
|------|------|-------------|--------|--------|
| display | 3.5rem (clamp to 2.25rem mobile) | 1.05 | 700 | display |
| h1 | 2.25rem | 1.1 | 700 | display |
| h2 | 1.75rem | 1.15 | 700 | display |
| h3 | 1.375rem | 1.2 | 600 | display |
| h4 | 1.125rem | 1.3 | 600 | display |
| body-lg | 1.125rem | 1.6 | 400 | body |
| body | 1rem | 1.6 | 400 | body |
| small | 0.875rem | 1.5 | 400 | body |
| overline | 0.75rem | 1.4 | 700 | body, uppercase, letter-spacing 0.08em, color ink |

## Radius tokens

```
--radius-sm:   6px    /* chips, small controls */
--radius:      8px    /* buttons, inputs (default) */
--radius-lg:   12px   /* cards, modals */
--radius-xl:   24px   /* large brand panels */
--radius-full: 9999px /* pills, badges, avatar */
```

## Spacing scale

4px base grid: `--space-1:4px … 2:8px, 3:12px, 4:16px, 5:20px, 6:24px, 8:32px, 10:40px, 12:48px, 16:64px, 20:80px`. Screens use these steps; section vertical rhythm defaults to `space-12`/`space-16`.

## Elevation (shadow) tokens

```
--shadow-sm:  0 1px 2px rgba(8,0,86,0.06)
--shadow:     0 4px 12px rgba(8,0,86,0.08)    /* cards */
--shadow-lg:  0 12px 32px rgba(8,0,86,0.14)   /* modals, popovers */
```
Shadows are tinted with navy (`ink`) rather than pure black, to sit in the brand.

## Motion tokens

```
--duration-fast:   120ms
--duration:        200ms
--duration-slow:   400ms  /* blob drift, hero */
--ease:            cubic-bezier(0.4, 0, 0.2, 1)
```
All motion gated by `@media (prefers-reduced-motion: reduce)` → `animation: none; transition-duration: 0.01ms`.

## Brand assets

- **Logo**: "Lab Livre" wordmark + leaf/heart glyph, white on purple header (`LabLivreLogo.tsx`).
- **Co-brand strip**: peach band "MAIS UM PROJETO POR" + QORA mark (entry surfaces only).
- **Blobs**: organic shapes in `ink`, `primary-light`, `success`, `accent` — decorative, `aria-hidden`, reduced-motion-static.

## State semantics (applies to all interactive components)

| State | Visual rule |
|-------|-------------|
| default | token fill/border per variant |
| hover | darken by one step (e.g. primary→primary-dark) |
| focus-visible | 2px ring in `primary` + 2px offset, always visible |
| active/pressed | primary-dark / inset |
| disabled | 50% opacity, `cursor: not-allowed`, no hover |
| error | `danger` border + message, `aria-invalid`, `aria-describedby` |
| loading | spinner + `aria-busy`, control disabled |
| empty | `EmptyState` (blob + message + optional action) |
