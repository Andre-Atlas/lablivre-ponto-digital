# Phase 1 Data Model: Frequência lançada por mentores

## Enums (novos)

```
StatusAluno:        ATIVO | DESLIGADO
StatusFrequencia:   PRESENTE | FALTA | JUSTIFICADO
Turno:              MANHA | TARDE      (já existente)
```

## User (alteração)

Campos existentes mantidos (`id, email, nome, tipo, role, turma_ou_equipe, oauth_provider, oauth_sub, senha_hash, patrimonio, ativo, admin_aprovado, criado_em, atualizado_em`).

- **+ `status: StatusAluno`** — aplicável a alunos (`tipo = ALUNO`), default `ATIVO`. Mentores/admins ignoram o campo.
- **Regra**: alunos (`tipo = ALUNO`) `senha_hash` MUST ser nula e NÃO autenticam.
- **Regra**: aluno tem exatamente uma turma (`turma_ou_equipe`), que deve existir em `config.turmas`.

## MentorTurma (nova — junção N–N)

| Campo | Tipo | Regras |
|-------|------|--------|
| id | UUID | PK |
| user_id | UUID FK → users | mentor (tipo STAFF ou role ADMIN/SUPER_ADMIN) |
| turma | String(100) | deve existir em `config.turmas` |
| criado_em | datetime | |

- Unicidade: (`user_id`, `turma`) único.
- Um mentor pode ter 1..N linhas (tipicamente 1 ou 2). Admin/super-admin: acesso a todas as turmas independentemente desta tabela.

## Frequencia (nova — agregado central)

| Campo | Tipo | Regras |
|-------|------|--------|
| id | UUID | PK |
| aluno_id | UUID FK → users | aluno avaliado (`tipo = ALUNO`) |
| turma | String(100) | turma do aluno no momento do lançamento |
| data | Date | dia do lançamento |
| turno | Turno | MANHA/TARDE |
| status | StatusFrequencia | PRESENTE/FALTA/JUSTIFICADO |
| mentor_id | UUID FK → users | autor do lançamento |
| atestado_documento | bytes \| null | documento anexado quando Falta justificada (apenas este turno) |
| atestado_filename | String \| null | |
| atestado_content_type | String \| null | |
| observacao | String \| null | opcional |
| criado_em / atualizado_em | datetime | |

- **Unicidade (idempotência)**: (`aluno_id`, `data`, `turno`) único → relançar faz upsert.
- **Transições de status**:
  - `PRESENTE` ⇄ `FALTA` (mentor altera).
  - `FALTA` → `JUSTIFICADO` ao atrelar atestado àquele turno.
  - `JUSTIFICADO` → `FALTA` ao remover o atestado.
  - Atestado só pode ser anexado quando o estado é `FALTA`/`JUSTIFICADO` (não em `PRESENTE`).
- **RBAC**: criar/alterar exige que `mentor_id` pertença à `turma` (via `mentor_turmas`) ou seja admin/super-admin; o `aluno_id` deve pertencer à mesma `turma`.
- Alunos `DESLIGADO` não entram nas listas de lançamento (não se criam novas `Frequencia` para eles); lançamentos antigos permanecem.

## Relações

- **Mentor N–N Turma** via `mentor_turmas`.
- **Aluno 1–1 Turma** via `users.turma_ou_equipe`.
- **Frequencia N–1 Aluno** e **N–1 Mentor**; escopada por `turma`.

## Entidades preservadas (histórico)

- `MedicalCertificate` / `CertificateDay` (feature 001): preservadas como histórico; o novo fluxo não cria mais atestados por período.
- `LearningOutcome` / avaliações (feature 002): inalteradas, apenas passam a filtrar alunos `ATIVO` e respeitar o escopo de turma do mentor.

## Entidades descartadas

- `Checkin` (autofrequência): dados descartados na migração; fluxo/rota removidos.

## Regras de validação (resumo)

- Aluno sem turma válida → rejeitar cadastro.
- Lançar frequência para turma fora do escopo do mentor → 403.
- Atestado em aluno `PRESENTE` → 400.
- Relançar mesmo (aluno, data, turno) → atualiza (não duplica).
- Exportações: incluem `JUSTIFICADO` por atestado; incluem alunos `DESLIGADO` apenas em relatórios históricos, marcados.
