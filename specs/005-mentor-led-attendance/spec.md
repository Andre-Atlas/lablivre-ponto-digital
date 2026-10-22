# Feature Specification: Frequência lançada por mentores

**Feature Branch**: `005-mentor-led-attendance`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "A frequência na verdade deve ser lançada pelos professores. Excluir função de autofrequência. Os alunos não podem fazer login, só os mentores. Os mentores estão atrelados a turmas: alguns estão atrelados a duas e outros a só uma. Os alunos ficam atrelados a só uma turma. Os alunos têm o seguinte status: Ativo e Desligado."

## Overview

Hoje a frequência é auto-registrada pelos próprios alunos (autofrequência: o aluno faz login e "bate o ponto" com geolocalização). Esta feature inverte o modelo: **a frequência passa a ser lançada pelos mentores (professores)**, os alunos deixam de ter login, e a relação entre pessoas e turmas é formalizada. Também passa a existir um **status do aluno** (Ativo/Desligado) para controlar quem está ativo no programa.

É uma mudança de modelo de domínio e de papéis (não apenas de interface): quem autentica, quem lança frequência, e como pessoas se vinculam a turmas.

## Clarifications

### Session 2026-10-15

- Q: A aba/tela separada de Atestados deve continuar existindo? → A: Não. Os atestados passam a ser atrelados no próprio lançamento da frequência; não há mais tela de Atestados.
- Q: Ao atrelar um atestado no lançamento, o que ele cobre? → A: Apenas o turno marcado naquele lançamento (para justificar vários dias, anexa-se um atestado em cada turno).
- Q: Como o mentor marca a frequência de uma turma numa data/turno? → A: Marcando cada aluno individualmente como Presente ou Falta (sem marcação em massa).
- Q: O que fazer com o histórico de ponto do modelo antigo (autofrequência)? → A: Descartar os check-ins antigos dos alunos.
- Q: Alunos Desligados aparecem em exportações/relatórios históricos? → A: Sim — ficam fora das listas ativas, mas aparecem nas exportações históricas marcados como Desligado.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mentor lança a frequência da turma (Priority: P1)

Como mentor, quero lançar a presença/falta dos alunos da(s) minha(s) turma(s) em uma data e turno, para que a frequência seja registrada por quem acompanha a turma — e não mais pelo próprio aluno.

**Why this priority**: É o coração da feature e substitui o mecanismo central do produto (o ponto do aluno). Sem isso, não há frequência.

**Independent Test**: Logar como mentor, escolher turma + data + turno, marcar alunos como presentes/faltantes e salvar; reabrir e confirmar que os lançamentos persistiram e aparecem nos relatórios/exportações.

**Acceptance Scenarios**:

1. **Given** um mentor atrelado a uma turma, **When** ele seleciona a turma, uma data e um turno, **Then** vê a lista de alunos ativos daquela turma para marcar presença ou falta.
2. **Given** a frequência lançada por um mentor, **When** um administrador exporta o relatório de frequência, **Then** os status refletem o que o mentor lançou (Presente/Falta/Justificado).
3. **Given** um aluno marcado como Falta com um atestado atrelado àquele turno no lançamento, **When** a frequência é apresentada/exportada, **Then** o turno aparece como Justificado em vez de Falta.

---

### User Story 2 - Fim da autofrequência e do login de aluno (Priority: P1)

Como responsável pelo sistema, quero remover a autofrequência e o login dos alunos, para que apenas mentores autentiquem e para que alunos sejam exclusivamente registros administrados.

**Why this priority**: É a contrapartida direta da US1 e remove um fluxo inteiro (ponto do aluno + autenticação de aluno). Precisa acontecer junto para o modelo ficar consistente.

**Independent Test**: Confirmar que não existe mais tela/fluxo de "bater ponto" pelo aluno, que alunos não conseguem logar nem se cadastrar, e que somente mentores (STAFF/ADMIN) entram na plataforma.

**Acceptance Scenarios**:

1. **Given** a plataforma, **When** alguém tenta autenticar como aluno, **Then** o acesso é negado (alunos não possuem credenciais).
2. **Given** a plataforma, **When** um usuário comum acessa, **Then** não há opção de autorregistro de frequência (a função de autofrequência não existe mais).
3. **Given** um mentor autenticado, **When** ele acessa a plataforma, **Then** tem acesso às funções de lançamento de frequência e gestão conforme seu papel.

---

### User Story 3 - Vínculo de mentores e alunos a turmas (Priority: P2)

Como administrador, quero vincular cada mentor a uma ou mais turmas (tipicamente uma ou duas) e cada aluno a exatamente uma turma, para que cada mentor atue somente nas suas turmas.

**Why this priority**: Define o escopo de acesso de cada mentor; necessário para a US1 funcionar com segregação correta, mas pode ser entregue logo após o fluxo básico.

**Independent Test**: Atribuir um mentor a duas turmas e outro a uma; confirmar que cada um só enxerga/lança frequência e avaliações das suas turmas, e que um aluno pertence a uma única turma.

**Acceptance Scenarios**:

1. **Given** um mentor atrelado a duas turmas, **When** ele lança frequência, **Then** pode escolher entre as duas turmas e apenas essas.
2. **Given** um mentor atrelado a uma turma, **When** ele tenta acessar dados de outra turma, **Then** o acesso é negado.
3. **Given** o cadastro de um aluno, **When** ele é salvo, **Then** fica vinculado a exatamente uma turma já cadastrada.

---

### User Story 4 - Status do aluno (Ativo / Desligado) (Priority: P2)

Como administrador ou mentor, quero marcar um aluno como Ativo ou Desligado, para que alunos desligados saiam dos fluxos ativos (frequência, avaliação, dashboards) sem perder o histórico.

**Why this priority**: Importante para manter listas limpas e dados corretos, mas o fluxo principal de frequência funciona antes disso.

**Independent Test**: Desligar um aluno e confirmar que ele não aparece mais nas listas de lançamento de frequência/avaliação da turma, que seu histórico permanece consultável/exportável, e que ele pode ser reativado.

**Acceptance Scenarios**:

1. **Given** um aluno Ativo, **When** é marcado como Desligado, **Then** deixa de aparecer nas listas de lançamento de frequência e avaliação.
2. **Given** um aluno Desligado, **When** um administrador consulta o histórico, **Then** os registros anteriores do aluno permanecem disponíveis.
3. **Given** um aluno Desligado, **When** é reativado, **Then** volta a aparecer nos fluxos ativos como Ativo.

---

### Edge Cases

- **Mentor sem turma**: um mentor ainda não atrelado a nenhuma turma não deve conseguir lançar frequência (lista vazia + orientação para o admin vincular uma turma).
- **Aluno desligado com atestado/histórico**: desligar não apaga atestados nem avaliações já registrados.
- **Frequência duplicada**: lançar frequência para a mesma turma/data/turno novamente deve atualizar o lançamento existente, não duplicar.
- **Aluno sem turma**: não deve ser possível (aluno exige turma); registros legados sem turma precisam de tratamento (ver Assumptions).
- **Mentor de duas turmas**: alternar entre turmas não deve misturar listas nem lançamentos.
- **Dados históricos de autofrequência**: os check-ins antigos dos alunos são descartados na transição (ver Clarifications).
- **Atestado em aluno Presente**: só é possível atrelar atestado quando o aluno está marcado como Falta.
- **Atestado em vários dias**: cobrir mais de um dia exige atrelar um atestado em cada turno de falta (não há mais atestado por período).
- **Desligar aluno já lançado como presente**: o lançamento histórico permanece; apenas some dos fluxos futuros.

## Requirements *(mandatory)*

### Functional Requirements

**Lançamento de frequência pelo mentor**

- **FR-001**: Mentores MUST conseguir lançar a frequência dos alunos de uma turma à qual estão atrelados, para uma data e um turno (manhã/tarde), marcando **cada aluno ativo individualmente** como Presente ou Falta (sem marcação em massa).
- **FR-002**: O sistema MUST tratar a frequência lançada pelo mentor como a fonte de verdade da presença (substituindo o cálculo baseado no auto-check-in do aluno).
- **FR-003**: Ao marcar um aluno como Falta, o mentor MUST poder atrelar um atestado àquele turno; o turno com atestado passa a "Justificado" em vez de "Falta". Cada atestado justifica **apenas o turno marcado** (para vários dias, atrela-se um atestado em cada turno).
- **FR-004**: NÃO MUST existir tela/aba separada de Atestados; o registro e o vínculo de atestados acontecem exclusivamente no fluxo de lançamento da frequência.
- **FR-005**: Relançar a frequência para a mesma turma/data/turno MUST atualizar os lançamentos existentes (e os atestados atrelados), sem criar duplicatas.

**Fim da autofrequência e do login de aluno**

- **FR-006**: O sistema MUST remover completamente a função de autofrequência (o aluno registrar o próprio ponto, incluindo captura de localização).
- **FR-007**: Alunos MUST NOT possuir credenciais nem conseguir autenticar; não deve existir login nem autorregistro de aluno.
- **FR-008**: Somente mentores (perfis de equipe/administração) MUST conseguir autenticar e acessar a plataforma.

**Vínculo pessoa–turma**

- **FR-009**: Cada mentor MUST poder ser atrelado a uma ou mais turmas (tipicamente uma ou duas); administradores gerenciam esses vínculos.
- **FR-010**: Cada aluno MUST ser atrelado a exatamente uma turma já cadastrada.
- **FR-011**: Um mentor MUST acessar e lançar frequência/avaliações apenas das turmas às quais está atrelado; administradores têm acesso a todas as turmas.

**Status do aluno**

- **FR-012**: Cada aluno MUST ter um status entre Ativo e Desligado; novos alunos começam como Ativo.
- **FR-013**: Alunos Desligados MUST ser excluídos por padrão das listas ativas (lançamento de frequência, avaliação de LOs, dashboards), preservando o histórico anterior do aluno.
- **FR-014**: Administradores/mentores MUST poder alternar o status de um aluno entre Ativo e Desligado (reativar inclusive).

**Preservação e consistência**

- **FR-015**: A feature MUST preservar os atestados e as avaliações já registrados. Os check-ins antigos de autofrequência (modelo anterior) MUST ser descartados — não são migrados nem mantidos.
- **FR-016**: Exportações e dashboards MUST passar a considerar a frequência lançada pelos mentores e o status do aluno; alunos Desligados MUST aparecer nas exportações históricas identificados como Desligado, mesmo estando fora das listas ativas.

### Key Entities

- **Mentor**: pessoa que autentica (perfil de equipe/administração), atrelada a uma ou mais turmas; lança frequência e avalia alunos das suas turmas.
- **Aluno**: registro administrado, sem login, atrelado a exatamente uma turma, com status Ativo ou Desligado.
- **Turma**: agrupamento já existente; relaciona-se com muitos mentores e muitos alunos (mentor N–N turma; aluno 1–1 turma).
- **Lançamento de frequência**: registro feito por um mentor para um aluno em uma data e turno, com estado Presente, Falta ou Justificado. Quando Falta, pode ter um atestado atrelado (que o torna Justificado para aquele turno).
- **Atestado**: documento anexado a um lançamento de Falta, justificando apenas aquele turno; não existe mais entidade/tela de atestado separada do lançamento.
- **Status do aluno**: Ativo (participa dos fluxos) ou Desligado (fora dos fluxos ativos; histórico e exportações históricas preservados).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos lançamentos de frequência são feitos por mentores; não existe mais nenhum caminho para o aluno registrar a própria frequência.
- **SC-002**: 0 alunos conseguem autenticar na plataforma; somente mentores entram.
- **SC-003**: Um mentor vê e lança frequência/avaliações exclusivamente para as turmas às quais está atrelado (0 vazamentos entre turmas), enquanto administradores veem todas.
- **SC-004**: Um mentor consegue lançar a frequência de uma turma (todos os alunos de um turno) em menos de 2 minutos.
- **SC-005**: Todo aluno pertence a exatamente uma turma e possui exatamente um status (Ativo/Desligado); alunos Desligados não aparecem em nenhuma lista ativa.
- **SC-006**: Atestados e avaliações já registrados são preservados na transição; os check-ins antigos de autofrequência são descartados conforme decidido, sem perda de atestados nem avaliações.
- **SC-007**: Relatórios/exportações de frequência refletem corretamente os lançamentos dos mentores e as justificativas por atestado.

## Assumptions

- "Mentor/professor" corresponde aos perfis que já autenticam hoje (equipe/administração); "aluno" é o registro administrado sem login. A feature remove qualquer autenticação de aluno que exista hoje.
- O cliente desktop de ponto do aluno (autofrequência) deixa de fazer sentido e é descontinuado/aposentado no escopo desta feature; não há novo cliente de aluno.
- A granularidade da frequência segue o modelo já existente de turnos (manhã/tarde) por data.
- "Desligado" é um status reversível (o aluno pode ser reativado) e não exclui dados — apenas remove o aluno dos fluxos ativos.
- Um mentor pode estar atrelado a mais de uma turma; os exemplos citam uma ou duas, mas o modelo não precisa impor um teto rígido de duas.
- Administradores/super-admins mantêm acesso a todas as turmas, independentemente de vínculo.
- Os check-ins antigos de autofrequência são descartados na transição (decisão em Clarifications); atestados e avaliações são preservados.
- O atestado deixa de ter tela própria e passa a ser atrelado por turno no fluxo de lançamento, justificando apenas o turno marcado (substitui o modelo de período/aba da feature de atestados anterior).

## Out of Scope

- Redesenho visual/identidade (já tratado em feature anterior).
- Novas métricas ou relatórios além de adequar os existentes ao novo modelo.
- Um novo aplicativo ou portal para alunos.
- Importação de uma nova base de alunos/turmas (usa-se a base já cadastrada).
