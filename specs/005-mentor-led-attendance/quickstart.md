# Quickstart: Frequência lançada por mentores

## Pré-requisitos
- Backend (FastAPI) + Postgres/sqlite com a nova migração aplicada; frontend (Vite).
- Pelo menos: 1 turma cadastrada, 1 mentor atrelado a essa turma, alguns alunos ATIVOS na turma.

## Executar
```bash
# backend
cd backend && alembic upgrade head && uvicorn app.main:app --reload
# frontend
cd web_admin && npm run dev
```

## Cenários de validação

### 1. Mentor lança frequência (US1)
- Logar como mentor → abrir **Frequência** → escolher turma + data + turno.
- Marcar cada aluno como Presente/Falta e salvar.
- Reabrir a mesma turma/data/turno → os lançamentos persistiram (sem duplicar).

### 2. Atestado no lançamento (clarificação)
- Marcar um aluno como **Falta** → anexar um atestado àquele turno → o status vira **Justificado**.
- Confirmar que não existe mais aba/tela separada de "Atestados".
- Remover o atestado → volta a **Falta**.

### 3. Fim da autofrequência e do login de aluno (US2)
- Confirmar que não há tela de "bater ponto" nem rota de auto-check-in.
- Tentar logar como aluno → negado. Apenas mentores entram.

### 4. Escopo por turma (US3)
- Mentor atrelado a 1 turma tenta acessar outra turma → 403.
- Mentor atrelado a 2 turmas alterna entre elas sem misturar listas.
- Admin vê todas as turmas.

### 5. Status do aluno (US4)
- Desligar um aluno → some das listas de lançamento/avaliação ATIVAS.
- Exportação histórica → o aluno Desligado aparece marcado como Desligado.
- Reativar → volta às listas ativas.

### 6. Migração / dados
- Após a migração: `mentor_turmas`, `frequencias`, `users.status` existem; check-ins antigos foram descartados; atestados e avaliações anteriores permanecem consultáveis.

## Done signal
Cenários 1–6 passam; E2E + axe verdes nas telas novas/alteradas; cobertura backend ≥80%; OpenAPI/README/ARCHITECTURE/CHANGELOG atualizados.
