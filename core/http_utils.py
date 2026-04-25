"""
Wrapper para llamadas httpx que normaliza errores de red en HTTPException.

Uso:
    response = await proxy_request(
        http.post("/api/...", json={...}, headers={...})
    )
"""
import logging
from typing import Coroutine, Any

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def proxy_request(coro: Coroutine[Any, Any, httpx.Response]) -> httpx.Response:
    """
    Ejecuta una coroutine de httpx y convierte errores de red en HTTPException.
    Los errores de negocio (4xx/5xx de la API remota) se delegan al llamador.
    """
    try:
        return await coro
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout al conectar con el servidor externo.")
    except httpx.RequestError as exc:
        logger.exception("Error de red al contactar la API externa: %s", exc)
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")
