"""Configurações e constantes do cliente desktop Ponto Digital."""

import os
from pathlib import Path

# URL base da API backend
API_BASE_URL: str = os.getenv("API_BASE_URL", "https://ponto-digital-api.run.app")

# Metadados da aplicação
APP_VERSION: str = "0.1.0"
APP_NAME: str = "Ponto Digital"

# Diretórios e arquivos de cache local
CACHE_DIR: Path = Path.home() / ".ponto-digital"
CACHE_DB: Path = CACHE_DIR / "cache.db"
SESSION_FILE: Path = CACHE_DIR / "session.json"

# Tempos e limites operacionais (em segundos)
AUTO_DISMISS_SECONDS: int = 120  # 2 minutos para fechamento automático
FEEDBACK_DISPLAY_SECONDS: int = 5  # Tempo de exibição de feedback visual
OFFLINE_RETRY_INTERVAL: int = 60  # Intervalo de retentativa para sincronização offline
MAX_RETRY_ATTEMPTS: int = 5  # Número máximo de tentativas de reenvio offline

# Atualizações automáticas
GITHUB_RELEASES_URL: str = "https://api.github.com/repos/OWNER/REPO/releases/latest"
