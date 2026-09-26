# Changelog

## [Unreleased]
### Added
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
