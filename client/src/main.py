"""Ponto de entrada do cliente desktop Ponto Digital."""

import logging
import platform
import sys
from pathlib import Path

import flet

from src.app import PontoDigitalApp
from src.config import APP_NAME, CACHE_DIR


def configure_environment() -> str:
    """Configura o ambiente da aplicação: cria diretório de cache, configura logging e detecta o SO.

    Retorna:
        str: Identificação do sistema operacional detectado.
    """
    # Cria o diretório de cache se não existir (~/.ponto-digital)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    log_path: Path = CACHE_DIR / "app.log"

    # Configuração de logging direcionado para ~/.ponto-digital/app.log e terminal
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Detecção do sistema operacional através de platform.system()
    sistema_operacional = platform.system()
    logging.info("Iniciando %s no sistema operacional: %s (%s)", APP_NAME, sistema_operacional, platform.release())
    logging.info("Diretório de cache: %s", CACHE_DIR)

    return sistema_operacional


def app_main(page: flet.Page) -> None:
    """Função alvo do Flet que cria uma janela com título 'Ponto Digital' e inicializa a interface."""
    page.title = "Ponto Digital"

    # Inicializa o gerenciador da aplicação e exibe tela inicial
    app = PontoDigitalApp(page)
    app.show_onboarding()


def main() -> None:
    """Ponto de entrada principal da aplicação desktop."""
    configure_environment()
    flet.app(target=app_main)


if __name__ == "__main__":
    main()
