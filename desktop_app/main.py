import flet as ft
from app.core.config import settings
from app.core.state import app_state
from app.core.api_client import api
from app.views.login_view import LoginView
from app.views.checkin_view import CheckinView
from app.views.onboarding_view import OnboardingView
from app.utils.network import get_current_mac

def main(page: ft.Page):
    page.title = settings.APP_TITLE
    page.window.width = 400
    page.window.height = 600
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT

    def show_error(msg):
        dlg = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(msg))
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def process_google_token(google_access_token: str):
        try:
            real_mac = get_current_mac()
            # Attempt login first
            resp = api.post("/api/v1/auth/onboarding", json={
                "oauth_token": google_access_token,
                "oauth_provider": "google",
                "tipo": "ALUNO",
                "device_mac": real_mac,
                "device_os": "macOS"
            })
            
            if resp.status_code == 200:
                data = resp.json()
                app_state.token = data["access_token"]
                page.go("/checkin")
            elif resp.status_code == 400 and "obrigat" in resp.text.lower():
                # User is new and missing required fields like patrimonio or turma
                app_state.temp_google_token = google_access_token
                page.go("/onboarding")
            elif resp.status_code == 201: # Just in case the backend lets it through
                data = resp.json()
                app_state.token = data["access_token"]
                page.go("/checkin")
            else:
                show_error(f"Erro de acesso (HTTP {resp.status_code}): {resp.text}")
                
        except Exception as ex:
            print("Erro de conexão:", ex)
            show_error("Backend offline ou inacessível")

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(LoginView(page, process_google_token))
        elif page.route == "/onboarding":
            page.views.append(OnboardingView(page))
        elif page.route == "/checkin":
            page.views.append(CheckinView(page))
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
