# 🖥️ Ponto Digital — Client Desktop

Aplicativo desktop nativo multiplataforma construído em **Python 3.11+** com a engine visual do **Flet (Flutter runtime)**. O client é responsável pelo registro rápido e intuitivo de ponto nas estações de trabalho dos residentes e colaboradores, contando com fila de contingência para operação offline e notificações de status de ponto.

---

## 🏛️ Estrutura de Diretórios

```
client/
├── assets/               # Ícones (.ico, .icns, .png), fontes e logotipos
├── build/                # Configurações intermediárias de compilação
├── scripts/              # Scripts de build e automação para OS específicos
│   ├── build.sh          # Script de empacotamento para macOS e Linux
│   └── build.ps1         # Script de empacotamento para Windows PowerShell
├── src/
│   ├── auth/             # Módulo de autenticação, armazenamento seguro de tokens
│   ├── checkin/          # Lógica de registro de ponto, regras de validação local
│   ├── hardware/         # Identificação de máquina, endereço MAC e telemetria
│   ├── platform_utils/   # Utilitários específicos de SO (bandeja, inicialização no boot)
│   ├── updater/          # Verificação de atualizações automáticas via GitHub Releases
│   └── ui/               # Telas, temas, diálogos e componentes Flet
│       └── main.py       # Ponto de entrada do aplicativo Desktop
├── tests/                # Testes unitários do client desktop
├── pyproject.toml        # Metadados do pacote Python
└── requirements.txt      # Dependências da aplicação client
```

---

## 📋 Pré-requisitos

### Pré-requisitos Gerais
- **Python 3.11** instalado.
- Gerenciador de pacotes **pip** e **git**.

### Dependências Específicas por Sistema Operacional

#### macOS
- Xcode Command Line Tools: `xcode-select --install`

#### Linux (Ubuntu/Debian)
O Flet necessita de bibliotecas gráficas do GTK e GStreamer:
```bash
sudo apt-get update
sudo apt-get install -y libgtk-3-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libmpv-dev
```

#### Windows
- Nenhuma dependência externa adicional necessária.

---

## 🛠️ Ambiente de Desenvolvimento

### 1. Criar e Ativar o Ambiente Virtual

```bash
cd client
python3.11 -m venv .venv

# No Linux/macOS:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuração Local (`.env`)

Crie um arquivo `.env` dentro da pasta `client/` com o seguinte conteúdo:

```ini
# URL base da API do Backend
API_BASE_URL=http://localhost:8000/api/v1

# Modo de depuração (ativa logs detalhados e hot reload)
DEBUG=true

# Nome da aplicação exibido na barra de título
APP_NAME=Ponto Digital - Residência
```

### 4. Executar em Modo de Desenvolvimento

```bash
# Execução direta com o interpretador Python
python -m src.ui.main

# Ou com recarregamento em tempo real do Flet
flet run src/ui/main.py
```

---

## 📦 Empacotamento e Build com PyInstaller / Flet

O aplicativo pode ser empacotado como um executável binário autocontido (não necessitando de Python pré-instalado na máquina do usuário final).

### Build no macOS
Gera um aplicativo `.app` (ou `.dmg`):
```bash
flet pack src/ui/main.py \
  --name "PontoResidencia" \
  --icon "assets/icon.icns" \
  --distpath "dist" \
  --product-name "Ponto Digital Residência" \
  --copyright "Copyright © 2026 Residência de Software"
```

### Build no Windows
Gera um executável `.exe`:
```powershell
flet pack src\ui\main.py `
  --name "PontoResidencia" `
  --icon "assets\icon.ico" `
  --distpath "dist" `
  --product-name "Ponto Digital Residência"
```

### Build no Linux
Gera um binário executável Linux:
```bash
flet pack src/ui/main.py \
  --name "PontoResidencia" \
  --icon "assets/icon.png" \
  --distpath "dist"
```

---

## 🚀 Scripts de Instalação e Automação

Os scripts utilitários localizados na pasta `client/scripts/` padronizam o fluxo de instalação local e empacotamento:

- **`scripts/build.sh`**: Limpa diretórios temporários, compila os arquivos binários e gera o pacote compactado `.tar.gz`.
- **`scripts/build.ps1`**: Script equivalente para Windows PowerShell que gera o pacote `.zip`.
- **`scripts/install.sh`**: Cria atalhos de inicialização no sistema (`.desktop` no Linux ou atalho no dock do macOS) e registra a inicialização automática no login do usuário.

---

## 🧪 Testes

Execute a suíte de testes do client:

```bash
pytest tests/ -v
```
