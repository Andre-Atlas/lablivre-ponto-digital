import flet as ft
import threading
import time

def main(page: ft.Page):
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", [ft.Text("Login Screen")]))
        else:
            page.views.append(ft.View("/checkin", [ft.Text("Checkin Screen")]))
        page.update()

    page.on_route_change = route_change
    page.go("/")

    def bg_task():
        time.sleep(2)
        print("Thread running go(/checkin)...")
        page.go("/checkin")

    threading.Thread(target=bg_task).start()

ft.app(target=main)
