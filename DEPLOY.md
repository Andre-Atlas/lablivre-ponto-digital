# Deploy (grátis): Neon + Render + Cloudflare Pages

Três peças, todas com plano gratuito:

| Peça | Serviço | O que roda |
|------|---------|------------|
| Banco | **Neon** | PostgreSQL serverless |
| Backend | **Render** (Docker) | FastAPI (`backend/Dockerfile` → `alembic upgrade head` + gunicorn/uvicorn) |
| Frontend | **Cloudflare Pages** | Build estático do Vite (`web_admin/dist`) |

> ⚠️ Planos gratuitos mudam com frequência — confirme os limites atuais. O backend no Render free **"dorme"** após ~15 min de inatividade (1ª requisição leva ~30–60s). O Neon também suspende e retoma rápido.

---

## 1) Banco — Neon
1. Crie um projeto em neon.tech → copie a **connection string**.
2. Converta para o formato **async + SSL** que o app usa:
   ```
   postgresql+asyncpg://USUARIO:SENHA@HOST/neondb?ssl=require
   ```
   - Troque `postgresql://` por **`postgresql+asyncpg://`**.
   - Troque `?sslmode=require...` por **`?ssl=require`** (o asyncpg não entende `sslmode`).
   - Use o endpoint **pooled** do Neon (o app já define `statement_cache_size=0`, compatível com o pooler).

## 2) Backend — Render
Opção A (Blueprint): **New + → Blueprint** apontando para este repo (ele lê o `render.yaml`).
Opção B (manual): **New + → Web Service** → runtime **Docker**, raiz `backend/`, health check `/api/v1/health`, plano **Free**.

Defina as variáveis de ambiente:
- `DATABASE_URL` = a URL do Neon do passo 1.
- `JWT_SECRET_KEY` = um segredo forte (o Blueprint gera automático).
- `CORS_ORIGINS` = a URL do frontend (preencha depois do passo 4), ex.: `https://ponto-digital.pages.dev`.

O deploy roda as migrações sozinho (`alembic upgrade head` no `CMD` do Dockerfile). Anote a URL do serviço, ex.: `https://ponto-digital-api.onrender.com`.

## 3) Primeiro acesso (criar o admin)
Como não há autocadastro, crie o 1º mentor **uma vez**. No **Shell** do serviço no Render (ou localmente com `DATABASE_URL` apontando pro Neon):
```bash
python scripts/create_admin.py --email voce@exemplo.com --nome "Seu Nome" --senha "umaSenhaForte"
```

## 4) Frontend — Cloudflare Pages
1. **Create application → Pages → Connect to Git** (este repo).
2. Configuração de build:
   - **Root directory:** `web_admin`
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
3. Variável de ambiente de build:
   - `VITE_API_URL` = `https://SEU-BACKEND.onrender.com/api/v1`
4. O arquivo `web_admin/public/_redirects` já cuida do roteamento SPA (react-router).

Anote a URL, ex.: `https://ponto-digital.pages.dev`.

## 5) Fechar o CORS
Volte no Render, defina `CORS_ORIGINS=https://ponto-digital.pages.dev` e faça **redeploy**. (Sem essa variável, o backend libera qualquer origem — ok só para testes.)

---

## Primeiros passos no app em produção
1. Login com o admin criado no passo 3.
2. **Cadastro → Turma**: cadastre as turmas (obrigatório antes de registrar alunos).
3. **Cadastro → Aluno**: registre os alunos (ou use um script de importação próprio).
4. **Pessoas** → editar um mentor → marque as **turmas do mentor**.
5. **Frequência**: lance a presença.

## Observações
- Uploads de atestado são salvos no **Postgres** (BYTEA), não em disco → compatível com o free tier stateless.
- A migração da feature 005 é destrutiva (apaga `checkins`), mas num banco **novo** ela só cria as tabelas — sem risco.
- Alternativas ao Render (se o cold start incomodar): **Koyeb** ou **Fly.io** (ambos leem o mesmo `backend/Dockerfile`).
