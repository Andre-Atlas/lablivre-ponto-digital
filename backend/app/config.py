from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Ponto Digital Multiplataforma"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: Optional[str] = None

    JWT_SECRET_KEY: str = "super_secret_key_change_me_in_prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    GOOGLE_CLIENT_ID: str = "your_google_client_id.apps.googleusercontent.com"
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    GEOFENCING_LAT: float = -15.98998
    GEOFENCING_LNG: float = -48.04487
    GEOFENCING_RADIUS_METERS: int = 200

    GOOGLE_SHEET_ID: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


def get_settings():
    return settings
