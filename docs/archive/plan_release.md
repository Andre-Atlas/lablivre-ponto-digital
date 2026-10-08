# Plano de Implementação: Automação de Releases do Cliente Desktop

## Objetivo
Criar uma esteira de Integração e Entrega Contínua (CI/CD) via GitHub Actions que compila automaticamente o aplicativo Desktop (Windows, Mac, Linux) usando Flet e publica uma "Release" oficial no GitHub sempre que criarmos uma tag de versão. Também atualizaremos os botões de download no portal web para apontarem diretamente para estes binários reais da última versão.

## User Review Required
- Como não temos a CLI do GitHub instalada localmente, o processo de release será totalmente orquestrado pela nuvem do GitHub (Actions).
- Preciso do seu "ok" para criar o script `.github/workflows/release-desktop.yml` e alterar os links no front-end React.

## Proposed Changes

### 1. Automação de Release (GitHub Actions)
#### [NEW] `.github/workflows/release-desktop.yml`
- Pipeline com matriz de sistemas operacionais (`windows-latest`, `macos-latest`, `ubuntu-latest`).
- Instala as dependências do `desktop_app`, executa os testes unitários via TDD.
- Empacota o app usando `flet pack main.py --name "PontoDigital"`.
- Zippa/Compacta o binário do macOS (pois `.app` é um diretório).
- Usa a action `softprops/action-gh-release` para atachar os 3 arquivos gerados a uma Release no GitHub automaticamente ao empurrarmos uma tag (ex: `v1.0.0`).

### 2. Atualização dos Links no Web Admin
#### [MODIFY] `web_admin/src/pages/Login.tsx`
#### [MODIFY] `web_admin/src/pages/Dashboard.tsx`
- Alterar o `href="#"` nos 3 botões de "Client (X)" para os links imutáveis de *latest release* do GitHub:
  - Windows: `https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest/download/PontoDigital.exe`
  - Mac: `https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest/download/PontoDigital-Mac.tar.gz`
  - Linux: `https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest/download/PontoDigital`

## Verification Plan
1. Farei o push dos novos links no frontend e do arquivo de workflow.
2. Criarei uma tag `v1.0.0` e farei o push para o repositório.
3. Você poderá acompanhar a compilação na aba **Actions** do seu GitHub.
4. Ao final, a tela que você mandou print com "There aren't any releases here" estará populada com a V1 e os executáveis prontos para download.
