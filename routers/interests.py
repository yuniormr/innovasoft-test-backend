from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional, List
import logging

from core.httpx_client import get_http_client
from schemas.clients import Interest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/Intereses", tags=["Intereses"])


def _bearer_header(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización requerido.")
    return authorization.removeprefix("Bearer ").strip()


@router.get("/Listado", response_model=List[Interest])
async def list_interests(token: str = Depends(_bearer_header)):
    http = get_http_client()

    try:
        response = await http.get(
            "/api/Intereses/Listado",
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception:
        logger.exception("Error obteniendo intereses")
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener los intereses.")

    return response.json()
