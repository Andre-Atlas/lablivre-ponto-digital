from getmac import get_mac_address
import platform
import subprocess

def get_current_mac() -> str:
    """Retorna o MAC Address principal da máquina."""
    mac = get_mac_address()
    return mac if mac else "00:00:00:00:00:00"

def get_current_wifi_info() -> dict:
    """
    Função stub. Em uma implementação completa usaria chamadas
    nativas de OS (ex: networksetup no macOS, netsh no Windows)
    para capturar o SSID e BSSID (MAC do roteador).
    """
    return {
        "ssid": "WIFI_MOCK",
        "bssids": ["00:11:22:33:44:55"]
    }
