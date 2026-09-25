import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    APP_TITLE = "Ponto Digital"
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

settings = Settings()
