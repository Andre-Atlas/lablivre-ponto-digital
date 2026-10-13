# Changelog

## [Unreleased]
### Added
- **Avaliação Semanal de Learning Outcomes (LOs)**: Mentores (STAFF/ADMIN) avaliam cada aluno (`ALUNO`) por semana, atribuindo um nível de 1 a 4 por objetivo de aprendizagem, com comentários; o formulário pré-preenche os últimos níveis conhecidos do aluno.
  - **Catálogo de LOs** gerenciável por administradores (criar, editar, desativar — histórico preservado).
  - **Dashboard** por turma/semana: avaliados vs pendentes, contagem por mentor, heatmap de níveis por LO e regressões em relação à semana anterior.
  - **Relatório semanal** exportável (CSV/Excel) com o nível de cada aluno por LO e os comentários.
  - Mentor restrito à própria turma; dados de avaliação visíveis apenas a mentores/administradores. Co-avaliação: o último nível prevalece por LO e os comentários de cada mentor são mantidos.
  - Novos endpoints: `GET/POST /api/v1/admin/los`, `PUT /api/v1/admin/los/{id}`, `GET /api/v1/admin/avaliacoes/config`, `GET /api/v1/admin/avaliacoes/prefill`, `GET/POST /api/v1/admin/avaliacoes`, `GET /api/v1/admin/avaliacoes/dashboard`, `GET /api/v1/admin/avaliacoes/export`.
- **Atestados Médicos**: Administradores podem registrar atestados médicos (documento + período contíguo) para alunos (`ALUNO`). Ao salvar, todos os turnos esperados do período sem check-in presente/atrasado real (FALTA ou já JUSTIFICADO) são marcados como justificados e **vinculados** ao atestado.
  - Vínculo persistente dia↔atestado (tabela `certificate_days`), rastreável nos dois sentidos e exibido no painel.
  - Documento armazenado no PostgreSQL (BYTEA, até 10 MB) e acessível apenas a administradores.
  - As exportações **CSV e Excel** passam a refletir os turnos justificados por atestado (o CSV foi reformulado para enumerar os turnos esperados do aluno, como o Excel).
  - Revogação de atestado reverte os turnos justificados exclusivamente por ele.
  - Novos endpoints: `POST/GET /api/v1/admin/certificados`, `GET /api/v1/admin/certificados/{id}`, `GET .../{id}/documento`, `POST .../{id}/revogar`.
- **Sistema de Permissões**: Adicionado modelo robusto com as roles `SUPER_ADMIN`, `ADMIN`, `STAFF` e `ALUNO`.
- **Desktop App (Python/Flet)**:
  - Adicionado suporte a inicialização automática com o sistema (Auto-startup).
  - Adicionado suporte a execução em background (System Tray).
  - Implementado sistema de pop-ups agendados para lembrete de check-in diário.
- **Web Dashboard (React)**:
  - Liberado recurso de check-in via web exclusivo para usuários da role `STAFF`.
  - Criada seção com links para download das aplicações Desktop cliente (Windows, macOS e Linux).
- **Relatórios**:
  - Exportação de planilhas Excel atualizada para incluir cálculos automáticos de 'Falta'.
  - Adicionada lógica de cruzamento de dados para identificar e classificar ausências como 'Justificado'.
