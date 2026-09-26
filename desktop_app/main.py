import flet as ft
import time
import threading
import schedule
from autostart import add_to_startup

def main(page: ft.Page):
    page.title = "Ponto Digital - Lab Livre"
    page.window.width = 400
    page.window.height = 600
    page.window.center()
    
    # Start hidden on boot (assuming we pass --hidden arg if started by OS, but let's just make it visible initially for manual opening, or hidden if triggered by OS)
    # For MVP, we'll just show it.
    
    def on_checkin(e):
        # Implementation of checkin...
        page.add(ft.Text("Ponto registrado com sucesso!", color="green"))
        page.update()
        
        # Hide after 3 seconds
        def hide():
            time.sleep(3)
            page.window.visible = False
            page.update()
        threading.Thread(target=hide).start()

    def popup_window():
        page.window.visible = True
        page.window.to_front()
        page.update()

    # Schedule the popups for Alunos
    schedule.every().monday.at("08:00").do(popup_window)
    schedule.every().monday.at("14:00").do(popup_window)
    schedule.every().wednesday.at("08:00").do(popup_window)
    schedule.every().wednesday.at("14:00").do(popup_window)
    schedule.every().friday.at("08:00").do(popup_window)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(30)
            
    threading.Thread(target=run_scheduler, daemon=True).start()

    page.add(
        ft.Column([
            ft.Text("Ponto Digital", size=30, weight="bold"),
            ft.Text("Seu horário de entrada chegou. Registre seu ponto agora!"),
            ft.ElevatedButton("Bater Ponto", on_click=on_checkin, width=200, height=50)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    add_to_startup()
    # Flet handles the main loop
    ft.app(target=main)
