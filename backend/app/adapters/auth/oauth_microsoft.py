from typing import Any, cast

import httpx


class InvalidTokenError(Exception):
    """Exceção levantada quando um token é inválido."""

    pass


async def verify_microsoft_token(token: str) -> dict[str, Any]:
    """
    Verifica um access token da Microsoft chamando a Graph API.
    Retorna o JSON da resposta contendo 'userPrincipalName' (email), 'displayName', 'id'.
    """
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return cast(dict[str, Any], response.json())
        else:
            raise InvalidTokenError(f"Token da Microsoft inválido. Status: {response.status_code}")
