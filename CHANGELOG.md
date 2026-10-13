# Changelog

## [Unreleased]
### Added
- **Avaliação Semanal de Learning Outcomes (LOs)**: Mentores (STAFF/ADMIN) avaliam cada aluno (`ALUNO`) por semana, atribuindo um nível de 1 a 4 por objetivo de aprendizagem, com comentários; o formulário pré-preenche os últimos níveis conhecidos do aluno.
  - **Catálogo de LOs** gerenciável por administradores (criar, editar, desativar — histórico preservado).
  - **Dashboard** por turma/semana: avaliados vs pendentes, contagem por mentor, heatmap de níveis por LO e regressões em relação à semana anterior.
  - **Relatório semanal** exportável (CSV/Excel) com o nível de cada aluno por LO e os comentários.
  - Mentor restrito à própria turma; dados de avaliação visíveis apenas a mentores/administradores. Co-avaliação: o último nível prevalece por LO e os comentários de cada mentor são mantidos.
  - Novos endpoints: `GET/POST /api/v1/admin/los`, `PUT /api/v1/admin/los/{id}`, `GET /api/v1/admin/avaliacoes/config`, `GET /api/v1/admin/avaliacoes/prefill`, `GET/POST /api/v1/admin/avaliacoes`, `GET /api/v1/admin/avaliacoes/dashboard`, `GET /api/v1/admin/avaliacoes/export`.
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
