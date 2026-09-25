class AppState:
    def __init__(self):
        self.token: str | None = None
        self.user_data: dict | None = None
        self.mac_address: str | None = None
        self.temp_google_token: str | None = None

# Instância global de estado da UI
app_state = AppState()
