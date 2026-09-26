import flet as ft
import threading
import json
from app.core.api_client import api
from app.utils.network import get_current_mac, get_current_wifi_info
from app.core.local_db import save_offline_checkin, get_unsynced_checkins, mark_as_synced

def CheckinView(page: ft.Page):
    status_text = ft.Text(
        "Pronto para registrar", 
        size=14, 
        weight=ft.FontWeight.W_400, 
        color=ft.Colors.BLUE_GREY_600
    )
    
    icon_container = ft.Container(
        content=ft.Icon(ft.Icons.FINGERPRINT, size=56, color=ft.Colors.WHITE),
        width=100,
        height=100,
        border_radius=50,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#D12A6A", "#F39200"]
        ),
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.4, "#D12A6A"),
            offset=ft.Offset(0, 8),
        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(bottom=30)
    )

    def show_msg(msg):
        dlg = ft.AlertDialog(
            content=ft.Text(msg, weight=ft.FontWeight.W_500),
            shape=ft.RoundedRectangleBorder(radius=16)
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def run_sync_background():
        unsynced = get_unsynced_checkins()
        if not unsynced:
            return
        
        success_count = 0
        for row in unsynced:
            cid, mac, ssid, bssids_json, ts = row
            try:
                bssids = json.loads(bssids_json)
                resp = api.post("/api/v1/checkin/", json={
                    "device_mac": mac,
                    "ssid": ssid,
                    "bssids": bssids,
                })
                if resp.status_code in [201, 409]:
                    mark_as_synced(cid)
                    success_count += 1
            except Exception:
                pass
                
        if success_count > 0:
            show_msg(f"{success_count} registros offline sincronizados!")

    def try_sync_now():
        threading.Thread(target=run_sync_background, daemon=True).start()

    def on_checkin_click(e):
        status_text.value = "Analisando localização..."
        status_text.color = ft.Colors.BLUE_GREY_600
        page.update()
        
        mac = get_current_mac()
        wifi = get_current_wifi_info()
        
        try:
            resp = api.post("/api/v1/checkin/", json={
                "device_mac": mac,
                "ssid": wifi["ssid"],
                "bssids": wifi["bssids"]
            })
            if resp.status_code == 201:
                data = resp.json()
                status_text.value = f"Acesso Liberado! Status: {data.get('status_checkin')}"
                status_text.color = "#00B9DE"
                icon_container.gradient = ft.LinearGradient(
                    colors=["#00B9DE", "#007A93"]
                )
                icon_container.shadow.color = ft.Colors.with_opacity(0.4, "#00B9DE")
                icon_container.content.name = ft.Icons.CHECK_CIRCLE
                try_sync_now()
            elif resp.status_code == 409:
                status_text.value = "Você já bateu o ponto neste turno."
                status_text.color = ft.Colors.BLUE_GREY_600
                icon_container.content.name = ft.Icons.INFO_OUTLINE
                try_sync_now()
            else:
                data = resp.json()
                err_msg = data.get('detail', resp.text)
                if "não aprovado" in err_msg.lower():
                    err_msg = "Aguardando aprovação da Coordenação."
                status_text.value = err_msg
                status_text.color = ft.Colors.RED_ACCENT_700
                icon_container.content.name = ft.Icons.WARNING_AMBER_ROUNDED
        except Exception as ex:
            print(f'ERRO CHECKIN: {ex}')
            import traceback; traceback.print_exc()
            save_offline_checkin(mac, wifi["ssid"], wifi["bssids"])
            status_text.value = "Offline. Ponto salvo no dispositivo."
            status_text.color = ft.Colors.AMBER_800
            
        page.update()

    checkin_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.VERIFIED_USER, color=ft.Colors.WHITE, size=20),
                ft.Text("Registrar Presença", color=ft.Colors.WHITE, weight=ft.FontWeight.W_600, size=15)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=300,
        height=54,
        border_radius=16,
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=["#D12A6A", "#B01E55"]
        ),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=14,
            color=ft.Colors.with_opacity(0.3, "#D12A6A"),
            offset=ft.Offset(0, 4),
        ),
        on_click=on_checkin_click,
        ink=True,
    )

    return ft.View(
        "/checkin",
        bgcolor="#F7F9FC",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        icon_container,
                        ft.Text(
                            "Lab Livre", 
                            size=28, 
                            weight=ft.FontWeight.BOLD, 
                            color="#1E293B"
                        ),
                        ft.Text(
                            "Controle de Acesso", 
                            size=14, 
                            weight=ft.FontWeight.W_300, 
                            color=ft.Colors.BLUE_GREY_400
                        ),
                        ft.Container(height=20),
                        ft.Container(
                            content=status_text,
                            padding=ft.padding.all(16),
                            border_radius=12,
                            bgcolor=ft.Colors.WHITE,
                            border=ft.border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=10,
                                color=ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                                offset=ft.Offset(0, 4),
                            ),
                            margin=ft.margin.only(bottom=30),
                            width=300,
                            alignment=ft.alignment.center
                        ),
                        checkin_button
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )
