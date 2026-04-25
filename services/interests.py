import logging

import httpx
from fastapi import HTTPException

from core.http_utils import proxy_request
from schemas.clients import Interest

logger = logging.getLogger(__name__)


async def list_interests(token: str, http: httpx.AsyncClient) -> list[Interest]:
    response = await proxy_request(
        http.get(
            "/api/Intereses/Listado",
            headers={"Authorization": f"Bearer {token}"},
        )
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al obtener los intereses.",
        )
    return [Interest(**item) for item in response.json()]
