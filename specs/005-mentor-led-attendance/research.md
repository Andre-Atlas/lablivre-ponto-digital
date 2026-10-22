# Phase 0 Research: Frequência lançada por mentores

## 1. Modelo de frequência: lançamento vs. cálculo por check-in

**Decisão**: Criar um agregado `Frequencia` persistido (uma linha por aluno/data/turno) com estado `PRESENTE | FALTA | JUSTIFICADO`, autor (mentor) e documento de atestado opcional por turno. A presença deixa de ser derivada da ausência de `Checkin`.

**Rationale**: O requisito inverte a fonte de verdade — quem registra é o mentor. Persistir o lançamento torna a presença explícita, auditável e idempotente (upsert por turma/data/turno). O modelo "falta = ausência de check-in" não tem mais sentido sem autofrequência.

**Alternativas**: (a) Reaproveitar `Checkin` com um flag "lançado por mentor" — rejeitado por carregar semântica e campos de geolocalização irrelevantes; (b) manter o cálculo e só adicionar overrides do mentor — rejeitado por duplicar a fonte de verdade.

## 2. Vínculo mentor–turma (N–N) e aluno–turma (1–1)

**Decisão**: Tabela de junção `mentor_turmas (user_id, turma)` para mentores; alunos continuam com uma única turma (campo `turma_ou_equipe`). Turma permanece identificada por nome (lista já cadastrada em `config.turmas`). RBAC: operações de frequência/avaliação validam, no servidor, se a turma alvo está entre as turmas do mentor (admins/super-admins ignoram a restrição).

**Rationale**: O spec diz "mentores atrelados a uma ou mais turmas; alunos a exatamente uma". Junção N–N cobre 1 ou 2 (ou mais) sem teto rígido. Reusar o cadastro de turmas existente evita nova entidade pesada.

**Alternativas**: (a) Entidade `Turma` com FK — mais "correto", porém maior migração; adiado (turmas hoje são nomes em `config`). (b) Campo multivalorado no `User` — rejeitado (não consultável/filtrável com segurança).

## 3. Status do aluno (Ativo/Desligado)

**Decisão**: Adicionar `enum StatusAluno { ATIVO, DESLIGADO }` e coluna `status` em `User` (default `ATIVO`), aplicável a alunos. Listas ativas (lançamento, avaliação, dashboards) filtram `status = ATIVO`; exportações históricas incluem Desligados com marcação.

**Rationale**: Status explícito é mais claro que reusar `ativo` (booleano já usado para "pode autenticar"). Desligar não apaga dados.

**Alternativas**: Reusar `ativo` — rejeitado por sobrecarga semântica (autenticação vs. participação no programa).

## 4. Atestado atrelado ao lançamento (por turno)

**Decisão**: O documento de atestado passa a ser anexado a um lançamento de `FALTA`, cobrindo **apenas aquele turno**, tornando-o `JUSTIFICADO`. Não há tela separada de Atestados. Registros de atestado por período já existentes (feature 001) são preservados como histórico, mas o novo fluxo não cria mais atestados por período.

**Rationale**: Decisão de produto (`/speckit-clarify`). Simplifica o modelo (documento por turno) e concentra tudo no lançamento.

**Alternativas**: Manter atestado por período + aba — rejeitado pelo usuário. Migrar atestados antigos para o novo formato por turno — desnecessário (preservados como histórico).

## 5. Remoção de autofrequência e login de aluno

**Decisão**: Remover `router_checkin` e a tela `Checkin.tsx`; remover do `router_auth` o registro/login de ALUNO; o login passa a emitir token apenas para mentores (STAFF/ADMIN/SUPER_ADMIN). O `desktop_app` de autofrequência é aposentado.

**Rationale**: Alunos são registros administrados sem credenciais; mentores são os únicos atores autenticados.

**Riscos/mitigação**: Garantir que nenhuma rota/claim antiga permita login de aluno; testes de autenticação negada para ALUNO.

## 6. Migração de dados (descarte de check-ins antigos)

**Decisão**: Migração Alembic que cria `mentor_turmas`, `frequencias`, `users.status`; **descarta** os dados de `checkins` do modelo de autofrequência (a tabela pode ser esvaziada/retirada do fluxo). Atestados e avaliações são preservados.

**Rationale**: Decisão explícita do usuário (`/speckit-clarify`). Registrado como desvio em Complexity Tracking.

**Riscos/mitigação**: Operação destrutiva — a migração deve ser revisada no PR; backup antes de aplicar em produção; cobrir com teste de migração em sqlite.

## Open questions

Nenhuma bloqueante — as decisões de alto impacto foram resolvidas em `/speckit-clarify`.
