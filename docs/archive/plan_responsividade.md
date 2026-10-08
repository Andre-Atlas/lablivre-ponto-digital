# Plano de Implementação: Responsividade Mobile

## Objetivo
Resolver os problemas de responsividade apontados na tela de Login (onde o texto, a logo e os downloads desaparecem no celular) e garantir que a interface fique tão impecável e funcional no mobile quanto é no desktop.

## User Review Required
Este plano altera a estrutura das páginas para empilhar os elementos no celular, liberando a rolagem vertical que antes era bloqueada no Login.

## Proposed Changes

### 1. Refatoração da Tela de Login (Mobile-First)
A tela atual esconde toda a coluna esquerda (Logo, Texto, Downloads) usando `hidden lg:flex`, deixando os usuários mobile apenas com o card de login flutuando.
Vamos empilhar os elementos de forma fluida no mobile e mantê-los lado a lado no desktop.

#### [MODIFY] `web_admin/src/pages/Login.tsx`
- Alterar o container principal para permitir rolagem vertical em telas menores: `overflow-x-hidden overflow-y-auto lg:overflow-hidden`.
- Remover o `hidden lg:flex` da área de marca (lado esquerdo).
- Centralizar o logo, texto e botões de download horizontalmente em telas móveis, mas manter alinhado à esquerda no Desktop (`text-center lg:text-left`, `mx-auto lg:mx-0`).
- Transformar as colunas flexíveis de `flex-1` puro para `w-full lg:flex-1` com `flex-col lg:flex-row` no container principal.
- Ajustar os espaçamentos (padding) para não ficar apertado ou espaçado demais no celular (ex: `px-6 pt-12 pb-6 lg:p-24`).
- Adicionar tamanhos relativos ao logo (`w-48 lg:w-64`) e ajustar a tipografia da manchete.

### 2. Polimento da Tela de Dashboard (Mobile)
A tela já possui alguma adaptação mobile, mas precisamos garantir que nada "vaze" ou quebre a estética.
#### [MODIFY] `web_admin/src/pages/Dashboard.tsx`
- Revisar a barra de navegação no topo (Header) para garantir que a Logo e os botões de ação não fiquem colados nas bordas do celular.
- Manter o foco no agrupamento e wrap inteligente dos botões da tabela (A busca, Exportar, Novo Admin). Eles já usam `flex-wrap`, mas checaremos o distanciamento (`gap`).

## Verification Plan
1. Rodar o projeto e usar o DevTools para simular visualização de celular (iPhone SE e Pixel 7).
2. Verificar se a logo, o texto e os links de download aparecem perfeitamente antes ou depois do card de login no mobile.
3. Verificar se o scroll funciona perfeitamente sem mostrar uma barra horizontal quebrando o fundo.
