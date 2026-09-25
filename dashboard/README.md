# 📊 Ponto Digital — Dashboard Web

Painel administrativo moderno, responsivo e seguro construído com **React 19**, **TypeScript**, **Vite** e **TailwindCSS**. Destinado a gestores, coordenadores e equipe de Recursos Humanos para acompanhamento de marcações de ponto em tempo real, visualização de espelhos de ponto, controle de inconsistências e parametrização do sistema.

---

## 🏛️ Estrutura de Diretórios

```
dashboard/
├── public/               # Ativos estáticos públicos (favicon, logos, manifest)
├── src/
│   ├── api/              # Clientes de comunicação HTTP (Axios/Fetch) com a API Backend
│   ├── auth/             # Contexto de autenticação, proteção de rotas e storage de tokens
│   ├── components/       # Componentes de UI reutilizáveis (botões, modais, tabelas, cards)
│   ├── pages/            # Telas da aplicação (Login, Dashboard, Colaboradores, Relatórios)
│   ├── types/            # Definições de tipos TypeScript compartilhados
│   ├── App.tsx           # Roteamento e provedores globais de contexto
│   ├── index.css         # Configurações do TailwindCSS e estilos globais
│   └── main.tsx          # Ponto de entrada do React 19
├── package.json          # Dependências e scripts do projeto
├── tailwind.config.js    # Configurações de tema, fontes e cores do TailwindCSS
├── tsconfig.json         # Configurações do compilador TypeScript
└── vite.config.ts        # Configurações do empacotador Vite
```

---

## 📋 Pré-requisitos

- **Node.js 20.x** (LTS) ou superior instalado.
- Gerenciador de pacotes **npm** (versão 10+) ou **pnpm**.

---

## 🛠️ Instalação e Execução Local

### 1. Instalar as Dependências

Na raiz do diretório `dashboard/`:

```bash
cd dashboard
npm install
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz da pasta `dashboard/` com base no exemplo:

```ini
# URL base da API do Backend
VITE_API_URL=http://localhost:8000/api/v1

# Título da aplicação
VITE_APP_TITLE=Ponto Digital - Gestão Residência
```

### 3. Iniciar o Servidor de Desenvolvimento

Execute o servidor local com Fast Refresh (HMR):

```bash
npm run dev
```

O painel estará disponível em:
👉 **[http://localhost:5173](http://localhost:5173)**

---

## 📦 Build para Produção

### Gerar os Arquivos Estáticos Otimizados

Para compilar e minificar a aplicação para deploy em produção:

```bash
npm run build
```

Os arquivos compilados serão gerados no diretório `dashboard/dist/`.

### Pré-visualizar o Build Localmente

Para simular o comportamento de produção antes do deploy:

```bash
npm run preview
```

---

## 🧪 Qualidade de Código e Formatação

```bash
# Executar verificação de tipos com o compilador TypeScript
npm run type-check

# Executar linter (ESLint)
npm run lint

# Formatar o código (Prettier)
npm run format
```

---

## 🚢 Deploy do Dashboard

Os arquivos estáticos gerados em `dist/` podem ser hospedados com alta disponibilidade em:
- **Google Cloud Storage + Cloud CDN** (recomendado para a arquitetura GCP do projeto)
- **Vercel** / **Netlify** / **Cloudflare Pages**
- Servidor **Nginx** ou contêiner Docker leve Alpine
