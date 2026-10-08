"""Interface do serviço de geolocalização."""

from abc import ABC, abstractmethod


class GeolocationService(ABC):
    """Port para validação de localização via Google Geolocation API."""

    @abstractmethod
    async def validar_localizacao(
        self,
        bssids: list[str],
        lat_centro: float,
        lng_centro: float,
        raio_metros: int,
        lat_user: float | None = None,
        lng_user: float | None = None,
    ) -> tuple[bool, float]:
        """Valida se os BSSIDs estão dentro do raio permitido.

        Returns:
            Tupla (esta_no_raio, distancia_metros).
        """
        ...
