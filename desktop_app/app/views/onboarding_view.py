import flet as ft
from app.core.api_client import api
from app.core.state import app_state
from app.utils.network import get_current_mac

def OnboardingView(page: ft.Page):
    turma_dropdown = ft.Dropdown(
        label="Turma ou Equipe",
        options=[
            ft.dropdown.Option("Turma 1"),
            ft.dropdown.Option("Turma 2")
        ],
        width=300,
        border_radius=12,
        focused_border_color="#00B9DE",
        border_color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        bgcolor=ft.Colors.WHITE,
        autofocus=True
    )
    
    patrimonio_field = ft.TextField(
        label="Número do Computador (ex: 01, 15)",
        width=300,
        border_radius=12,
        focused_border_color="#00B9DE",
        border_color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        bgcolor=ft.Colors.WHITE,
    )
    
    error_text = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.RED_ACCENT_700, visible=False)

    icon_container = ft.Container(
        content=ft.Icon(ft.Icons.PERSON_ADD_ALT_1, size=40, color=ft.Colors.WHITE),
        width=80,
        height=80,
        border_radius=40,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#F39200", "#D87D00"]
        ),
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=16,
            color=ft.Colors.with_opacity(0.3, "#F39200"),
            offset=ft.Offset(0, 6),
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=16)
    )

    def submit_onboarding(e):
        if not turma_dropdown.value or not patrimonio_field.value:
            error_text.value = "Preencha todos os campos obrigatórios."
            error_text.visible = True
            page.update()
            return

        error_text.visible = False
        page.update()

        real_mac = get_current_mac()
        
        try:
            resp = api.post("/api/v1/auth/onboarding", json={
                "oauth_token": app_state.temp_google_token,
                "oauth_provider": "google",
                "tipo": "ALUNO",
                "turma_ou_equipe": turma_dropdown.value,
                "patrimonio": patrimonio_field.value,
                "device_mac": real_mac,
                "device_os": "macOS"
            })
            
            if resp.status_code in [200, 201]:
                data = resp.json()
                app_state.token = data["access_token"]
                app_state.temp_google_token = None
                page.go("/checkin")
            else:
                error_text.value = f"Falha no registro: {resp.text}"
                error_text.visible = True
                page.update()
                
        except Exception as ex:
            error_text.value = "Servidor inacessível no momento."
            error_text.visible = True
            page.update()

    submit_button = ft.Container(
        content=ft.Text("Concluir e Acessar", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600, size=15),
        width=300,
        height=54,
        border_radius=16,
        alignment=ft.alignment.center,
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=["#00B9DE", "#007A93"]
        ),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=14,
            color=ft.Colors.with_opacity(0.3, "#00B9DE"),
            offset=ft.Offset(0, 4),
        ),
        on_click=submit_onboarding,
        ink=True,
    )

    return ft.View(
        "/onboarding",
        bgcolor="#F7F9FC",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        icon_container,
                        ft.Text("Finalizar Cadastro", size=24, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ft.Text(
                            "Como é seu primeiro acesso, precisamos de\nmais alguns dados da sua máquina.", 
                            text_align=ft.TextAlign.CENTER, 
                            color=ft.Colors.BLUE_GREY_500,
                            size=14
                        ),
                        ft.Container(height=24),
                        turma_dropdown,
                        ft.Container(height=4),
                        patrimonio_field,
                        ft.Container(height=16),
                        error_text,
                        submit_button,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )
