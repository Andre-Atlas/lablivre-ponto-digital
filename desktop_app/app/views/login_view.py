import flet as ft
import urllib.parse
from app.core.config import settings
from app.utils.oauth_server import listen_for_oauth_callback

def LoginView(page: ft.Page, on_token_received):
    status_text = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.RED_ACCENT_700)
    
    icon_container = ft.Container(
        content=ft.Icon(ft.Icons.LOCK_OUTLINE, size=48, color=ft.Colors.WHITE),
        width=90,
        height=90,
        border_radius=45,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#00B9DE", "#007A93"]
        ),
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.3, "#00B9DE"),
            offset=ft.Offset(0, 8),
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=24)
    )

    def auth_callback(access_token):
        status_text.value = "Autenticando no servidor..."
        status_text.color = ft.Colors.BLUE_GREY_600
        page.update()
        on_token_received(access_token)

    def on_login_click(e):
        status_text.value = "Aguardando login no navegador..."
        status_text.color = ft.Colors.BLUE_GREY_600
        page.update()
        
        listen_for_oauth_callback(auth_callback)
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&response_type=code&scope=openid%20email%20profile&redirect_uri=http://127.0.0.1:8550/oauth_callback"
        page.launch_url(auth_url)

    login_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Image(src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg", width=20, height=20),
                ft.Text("Entrar com Conta Google", color="#1E293B", weight=ft.FontWeight.W_600, size=15)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12
        ),
        width=300,
        height=54,
        border_radius=16,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        on_click=on_login_click,
        ink=True,
    )

    return ft.View(
        "/",
        bgcolor="#F7F9FC",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        icon_container,
                        ft.Text("Ponto Digital", size=28, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ft.Text(
                            "Acesso exclusivo para membros do Lab Livre", 
                            size=14, 
                            weight=ft.FontWeight.W_400, 
                            color=ft.Colors.BLUE_GREY_500,
                            text_align=ft.TextAlign.CENTER,
                            width=260
                        ),
                        ft.Container(height=32),
                        login_button,
                        ft.Container(height=16),
                        status_text
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )
