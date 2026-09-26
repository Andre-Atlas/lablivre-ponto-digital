# Ponto Digital (Residência)

Sistema completo de controle de ponto e gestão de presença, projetado para controle de check-in/check-out de residentes e staff.

## 🚀 Visão Geral

O **Ponto Digital** é composto por três frentes principais:
1. **API Backend**: Motor de regras de negócio, autenticação e relatórios.
2. **Web Dashboard (React)**: Painel administrativo para visualização de relatórios, gestão de usuários, exportação de planilhas e download de clientes.
3. **Desktop App (Python/Flet)**: Cliente residente nas máquinas locais que roda em background (System Tray) para notificações e registro de ponto rápido.

## ✨ Novidades e Funcionalidades

- **Sistema de Permissões (Roles)**: Estrutura robusta baseada em cargos: `SUPER_ADMIN`, `ADMIN`, `STAFF` e `ALUNO`.
- **Desktop App Autônomo**: Início automático com o sistema operacional, fixação na bandeja do sistema e pop-ups agendados para lembretes automáticos.
- **Check-in via Dashboard**: Exclusivo para usuários com permissão `STAFF`.
- **Exportação Inteligente para Excel**: Cálculo proativo de faltas em dias obrigatórios e integração de lógica com o status 'Justificado'.
- **Distribuição de Clientes**: Links de download para Windows, macOS e Linux disponíveis diretamente na dashboard.

## 📥 Download e Instalação

Os instaladores do **Desktop App** estão disponíveis na tela inicial do **Web Dashboard** ou através da seção [Releases](https://github.com/Andre-Atlas/lablivre-ponto-digital/releases) no GitHub.
- **Windows**: Baixe o `.exe` e execute o instalador.
- **macOS**: Baixe o `.dmg` ou `.app`.
- **Linux**: Baixe o `.AppImage` ou executável Linux.
*(A aplicação é atualizada via hotfixes disponibilizados nas releases oficiais).*

## 📖 Navegação da Documentação

- [Arquitetura do Sistema](ARCHITECTURE.md)
- [Changelog Historico](CHANGELOG.md)
