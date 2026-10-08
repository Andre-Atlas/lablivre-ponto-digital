from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CheckinRequest(BaseModel):
    device_mac: Optional[str] = None
    ssid: Optional[str] = None
    bssids: Optional[List[str]] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class CheckinResponse(BaseModel):
    status_checkin: str
    turno: str
    mensagem: str
    hora_registrada: datetime
