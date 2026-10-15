# web_admin — Painel Lab Livre (React + TypeScript + Vite)

Frontend do Ponto Digital. React 19 + Vite + Tailwind CSS v4, estilizado com o
**Design System Lab Livre**.

## Scripts

```bash
npm install
npm run dev        # servidor de desenvolvimento (http://localhost:5173)
npm run build      # typecheck (tsc -b) + build de produção (vite)
npm run lint       # oxlint
npx playwright test # E2E + acessibilidade (requer @playwright/test e a stack ativa)
```

## Design System

A identidade visual é a do Lab Livre (derivada da referência "Design V3"). Ver a
especificação em `../specs/004-lab-livre-design-system/`.

### Tokens (fonte única de verdade)

Todos os tokens vivem no bloco `@theme` de [`src/index.css`](src/index.css)
(abordagem CSS-first do Tailwind v4 — **não há `tailwind.config.js`**):

- **Cores**: `primary` (roxo `#7023E8`), `primary-dark`/`primary-light`, `accent`
  (laranja), `accent-pink`, `ink` (navy `#080056`), `success`, `danger`,
  superfícies `bg` (lavanda), `peach`, `surface` (branco) e a rampa neutra
  (`text`, `muted`, `border`). Use sempre utilitários de token (`bg-primary`,
  `text-ink`, `border-border`…) — **nunca** cores hex fixas na marcação.
- **Tipografia**: `--font-display` (**Poppins**, títulos) e `--font-body`
  (**Inter**, corpo/UI). As fontes são **auto-hospedadas** via `@fontsource`
  (nenhuma requisição a CDN externo em runtime). Classes utilitárias: `.display`
  (hero) e `.eyebrow` (rótulo sobre o título).
- **Forma/elevação/motion**: `rounded-card`/`rounded-pill`, `shadow-card`/
  `shadow-pop`, e reset global de animação sob `prefers-reduced-motion`.

### Componentes

Biblioteca reutilizável em [`src/components/ui/`](src/components/ui) (barril em
`ui/index.ts`): `Button`, `Card`, `Input`, `Select`, `Textarea`, `Badge`,
`Table`, `Modal`, `Tabs`, `Alert`, `ToastProvider/useToast`, `PageHeader`,
`StatCallout`, `Blob`, `EmptyState`. Chrome compartilhado: `AppHeader`,
`AppFooter`, `LabLivreLogo`.

Contratos de props em `../specs/004-lab-livre-design-system/contracts/components.md`.

### Styleguide

Rota de desenvolvimento **`/styleguide`** renderiza todos os componentes em suas
variantes e estados — use para revisão visual e regressão.

### Boas práticas aplicadas

- Tema **claro único** (sem dark mode).
- Contraste **WCAG AA** (verificado com axe), foco visível por teclado, semântica
  ARIA em Modal/Tabs/Toast, layout responsivo (~375px → desktop) e
  `prefers-reduced-motion` honrado.
- "Expressivo na entrada, sóbrio nos dados": branding lúdico (blobs, hero) em
  Login/Check-in/estados vazios; telas densas (tabelas/formulários) permanecem
  limpas e legíveis.
