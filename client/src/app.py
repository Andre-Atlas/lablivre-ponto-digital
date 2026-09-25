"""Esqueleto da aplicação Flet e gerenciador de navegação de telas."""

import logging
import flet as ft

from src.config import APP_NAME

logger = logging.getLogger(__name__)


class PontoDigitalApp:
    """Gerencia a navegação e o ciclo de vida das páginas da aplicação Ponto Digital."""

    def __init__(self, page: ft.Page) -> None:
        """Inicializa o aplicativo com a página principal do Flet.

        Args:
            page: Objeto ft.Page gerenciado pelo Flet runtime.
        """
        self.page = page
        self.page.title = APP_NAME
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        logger.info("PontoDigitalApp inicializado.")

    def show_onboarding(self) -> None:
        """Exibe a tela inicial de onboarding / pareamento de dispositivo."""
        logger.info("Renderizando tela de Onboarding.")
        self.page.clean()
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Boas-vindas ao Ponto Digital", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Tela de Onboarding / Pareamento do Terminal", size=14),
                    ft.ElevatedButton(
                        text="Acessar Registro de Ponto",
                        on_click=lambda _: self.show_checkin(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
        self.page.update()

    def show_checkin(self) -> None:
        """Exibe a tela de registro de ponto (Check-in / Check-out)."""
        logger.info("Renderizando tela de Check-in.")
        self.page.clean()
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Registro de Ponto", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Aproxime seu crachá RFID ou insira suas credenciais", size=14),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                text="Simular Sucesso",
                                on_click=lambda _: self.show_status("Ponto registrado com sucesso!"),
                            ),
                            ft.OutlinedButton(
                                text="Voltar ao Onboarding",
                                on_click=lambda _: self.show_onboarding(),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
        self.page.update()

    def show_status(self, status: str) -> None:
        """Exibe tela de feedback com o status da operação realizada.

        Args:
            status: Mensagem descritiva do status ou resultado do registro.
        """
        logger.info("Renderizando tela de Status: %s", status)
        self.page.clean()
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Status do Registro", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(status, size=16),
                    ft.ElevatedButton(
                        text="Novo Registro",
                        on_click=lambda _: self.show_checkin(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
        self.page.update()
