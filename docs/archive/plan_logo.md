# Plano de Implementação: Atualização da Logo e Favicon

## Objetivo
Atualizar a logo do dashboard para o novo design fornecido e configurar o ícone da borboleta como favicon do navegador. A nova logo deve ter o fundo transparente e se adaptar perfeitamente aos temas Claro e Escuro (SVG dinâmico com `currentColor`).

## User Review Required
Nenhuma decisão drástica, mas preciso da sua aprovação neste plano para injetar a nova logo vetorial (SVG) no código.

## Open Questions
Você prefere que o favicon seja roxo (como na segunda imagem) ou que siga o padrão do sistema (preto no modo claro e branco no modo escuro)? Vou assumir um favicon SVG que se adapta ao sistema (ou na cor roxa primária `#6b21a8`) para garantir a melhor visibilidade nas abas do navegador.

## Proposed Changes

### 1. Novo Componente SVG (Logo Completa)
Substituir as antigas imagens PNG (clara e escura) por um SVG inline responsivo no componente `LabLivreLogo.tsx`.
#### [MODIFY] `web_admin/src/components/LabLivreLogo.tsx`
```tsx
export function LabLivreLogo({ className = "" }: { className?: string }) {
  // A logo em SVG puro usa fill="currentColor", mudando de preto para branco
  // de acordo com a classe "text-slate-900 dark:text-white" herdada ou passada via className.
  return (
    <svg 
      className={`block text-slate-900 dark:text-white ${className}`} 
      viewBox="0 0 800 300"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Paths exatos extraídos do arquivo media_1790875925152.jpg */}
    </svg>
  );
}
```

### 2. Atualização do Favicon
Substituir o favicon antigo pela versão contendo apenas o ícone da borboleta.
#### [MODIFY] `web_admin/public/favicon.svg` (ou `favicon.ico`)
Criar o arquivo com o vector apenas do ícone principal, aplicando a cor de destaque (roxa/magenta) para dar legibilidade na aba do navegador.
#### [MODIFY] `web_admin/index.html`
Garantir que a tag `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />` esteja apontando para o arquivo correto.

## Verification Plan

### Manual Verification
1. Abrir a página de Login e o Dashboard (localhost).
2. Alternar entre Dark e Light mode para garantir que o texto "Lab Livre" e o ícone fiquem visíveis (pretos no claro, brancos no escuro).
3. Olhar a aba do navegador para verificar se o Favicon foi atualizado.
