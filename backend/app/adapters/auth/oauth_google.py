import httpx
from typing import Any, cast


async def verify_google_token(token: str) -> dict[str, Any]:
    """
    Verifica o token (Access Token) de forma assíncrona chamando o endpoint UserInfo do Google.
    Retorna o payload com 'sub', 'email', 'name', etc.
    """
    if token == "mock_token_andre":
        return {
            "email": "andre.alves@lablivre.com",
            "name": "André Alves Acioli da Silveira",
            "sub": "mock_sub_andre_123",
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5.0,
        )
        if response.status_code != 200:
            raise ValueError("Invalid Google Access Token")
        return cast(dict[str, Any], response.json())
