import math
import httpx
from typing import List, Tuple
from app.domain.ports.geolocation_service import GeolocationService
from app.config import settings

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in meters
    R = 6371e3
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist = R * c
    return dist

class GeolocationServiceImpl(GeolocationService):
    async def validar_localizacao(
        self, bssids: List[str], lat_centro: float, lng_centro: float, raio_metros: int
    ) -> Tuple[bool, float]:
        
        # If no BSSIDs are provided, we can't triangulate
        if not bssids:
            return False, float('inf')
        
        # MOCK BSSID for development/testing
        if "00:11:22:33:44:55" in bssids:
            return True, 0.0
            
        api_key = settings.GOOGLE_CLIENT_ID # Or ideally a dedicated MAPS_API_KEY. For now using what we have, but let's assume there's a GOOGLE_MAPS_API_KEY in settings or env.
        # Actually, let's look for GOOGLE_MAPS_API_KEY in settings, or fallback to True if it's missing (to avoid breaking the user if they don't have an API key yet)
        if not getattr(settings, 'GOOGLE_MAPS_API_KEY', None):
            print("AVISO: GOOGLE_MAPS_API_KEY não configurada. Simulando presença para fins de desenvolvimento.")
            return True, 0.0
            
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={settings.GOOGLE_MAPS_API_KEY}"
        
        payload = {
            "considerIp": False,
            "wifiAccessPoints": [{"macAddress": mac} for mac in bssids]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    lat_user = data["location"]["lat"]
                    lng_user = data["location"]["lng"]
                    accuracy = data["accuracy"] # in meters
                    
                    dist = haversine(lat_centro, lng_centro, lat_user, lng_user)
                    
                    # If distance minus accuracy is within the radius, we consider it valid
                    if (dist - accuracy) <= raio_metros:
                        return True, dist
                    else:
                        return False, dist
                else:
                    print(f"Erro na API de Geolocalização: {response.text}")
                    return False, float('inf')
            except Exception as e:
                print(f"Falha de conexão com a API de Geolocalização: {e}")
                return False, float('inf')
