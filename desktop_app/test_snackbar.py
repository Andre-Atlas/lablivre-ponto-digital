import flet as ft
def main(page: ft.Page):
    try:
        page.open(ft.SnackBar(ft.Text("Test")))
        print("Success!")
    except Exception as e:
        print("Crash:", e)
ft.app(target=main)
