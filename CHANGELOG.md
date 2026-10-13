# Changelog

## [Unreleased]
### Added
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
