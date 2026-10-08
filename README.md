# Ponto Digital - LabLivre UnB

![Versão](https://img.shields.io/badge/version-1.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Compatible-326CE5?logo=kubernetes&logoColor=white)

O **Ponto Digital Multiplataforma** é o sistema oficial de registro de frequência e gerência de horários desenvolvido para o LabLivre (UnB - Campus Gama). Ele permite que alunos e staff registrem entradas e saídas diárias, enquanto oferece um Painel Administrativo avançado para professores/supervisores gerenciarem equipes, aprovarem horas, baixarem planilhas e organizarem o laboratório físico.

## 🚀 Funcionalidades

### Para os Usuários (Alunos / Staff)
* **Check-in Dinâmico:** Registro fácil de chegada e saída do laboratório físico.
* **Cálculo de Horas:** Acompanhamento transparente do saldo e carga horária já realizada.
* **Perfil Interativo:** Edição autônoma de nome de exibição e troca segura de senha (auditoria e hash).
* **UI Responsiva e Temática:** Adapta-se automaticamente a modo Claro/Escuro (Light/Dark Mode).

### Para os Administradores
* **Gestão de Controle:** Painel administrativo interativo para visualização em tempo real de quem está no LabLivre.
* **Ações em Massa (Bulk Actions):** Autorização ou Justificativa de ponto de vários usuários com 1 único clique via Checkboxes.
* **Exportação Avançada (Relatórios):** Geração de planilhas Excel e CSV customizadas (Filtráveis por: Data Específica, Turma/Equipe, Turno, Tipo de Usuário).
* **Gestão de Usuários:** Edição de perfil de qualquer aluno (Turma, Número de Patrimônio da Máquina alocada, Nível de Acesso).

---

## 🏗️ Estrutura do Repositório

O repositório foi organizado em microsserviços para facilitar o deploy isolado:

```text
├── backend/       # API Backend (Python / FastAPI / SQLAlchemy Async)
├── web_admin/     # Frontend Web e Painel Admin (React / Vite / Tailwind)
├── k8s/           # Manifestos de Infraestrutura em Kubernetes (Pronto para Prod)
├── docs/          # Arquivos de Documentação e Imagens de Referência
├── scripts/       # Scripts utilitários de manutenção e migrações isoladas
└── desktop_app/   # Cliente Windows/Linux legados para Pontos Físicos Locais
```

👉 **[Leia a Documentação de Arquitetura Completa Aqui (ARCHITECTURE.md)](docs/ARCHITECTURE.md)**

---

## 🛠️ Como Executar Localmente

### Pré-requisitos
* **Docker** e **Docker Compose** instalados.

### 1. Preparando o Ambiente
Crie um arquivo `.env` na pasta principal baseado nos requisitos:

```ini
DATABASE_URL=postgresql+asyncpg://seu_usuario:sua_senha@db:5432/ponto_digital
JWT_SECRET_KEY=uma-chave-super-secreta-para-local
ENVIRONMENT=development
```
*(Nota: O `docker-compose.yml` já configura variáveis locais, portanto o `.env` é apenas para substituir comportamentos, se desejado)*

### 2. Subindo com o Docker Compose
No terminal, rodando na pasta raiz do projeto:

```bash
docker-compose build
docker-compose up -d
```

* **Frontend (Aplicação Web):** Estará disponível em `http://localhost:5173` (porta mapeada do contêiner para 8080 interno).
* **Backend (Documentação Swagger):** Estará disponível em `http://localhost:8000/docs`.

### 3. Criando o 1º Administrador
Com os contêineres rodando, você pode usar um dos scripts da pasta `scripts/archive` para injetar o primeiro Super Admin diretamente no banco local, se não quiser criar pela tela e ir no banco alterar o cargo manualmente.

---

## 🌩️ Implantação Cloud Native (Produção)

Este projeto não é "apenas local". A estrutura foi toda adaptada (Usuários não-root nos Dockerfiles, Gunicorn Multithreading, Ingress Rounting) para ambientes complexos.

### Opção 1: Kubernetes (Cluster próprio ou EKS/GKE)
Dentro do diretório `k8s/` estão todos os manifestos já preparados:
1. Adicione a sua `DATABASE_URL` (recomendamos uso de Supabase ou Neon para bancos na nuvem) no arquivo `k8s/02-configmap-secrets.yaml`.
2. Aplique a configuração: `kubectl apply -f k8s/`.

### Opção 2: Vercel + Render
A arquitetura de pastas também permite vincular o repositório diretamente:
- **Vercel:** Aponte para a Root Directory `web_admin`.
- **Render:** Crie um "Web Service" em Docker apontando para o subdiretório `backend/`.

---
**Equipe Responsável:** Andre Atlas / LabLivre UnB
