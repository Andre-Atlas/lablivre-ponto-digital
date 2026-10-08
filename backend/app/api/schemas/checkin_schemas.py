from datetime import datetime

from pydantic import BaseModel


class CheckinRequest(BaseModel):
    device_mac: str | None = None
    ssid: str | None = None
    bssids: list[str] | None = None
    lat: float | None = None
    lng: float | None = None


class CheckinResponse(BaseModel):
    status_checkin: str
    turno: str
    mensagem: str
    hora_registrada: datetime
