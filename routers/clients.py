from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional, List
from datetime import datetime, timezone
import logging

from core.httpx_client import get_http_client
from core.database import get_db
from schemas.clients import (
    ClientListRequest,
    ClientListItem,
    ClientDetail,
    ClientCreateRequest,
    ClientUpdateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/Cliente", tags=["Clientes"])


def _bearer_header(authorization: Optional[str] = Header(default=None)) -> str:
    """Extrae y valida el Bearer token del header Authorization."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización requerido.")
    return authorization.removeprefix("Bearer ").strip()


async def _audit(db, accion: str, usuario: str, cliente_id: str, resultado: int) -> None:
    """Registra una operación CRUD en la colección `operaciones`."""
    doc = {
        "accion": accion,
        "usuario": usuario,
        "cliente_id": cliente_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "resultado": resultado,
    }
    await db.operaciones.insert_one(doc)


async def _get_username_from_token(token: str, db) -> str:
    """Recupera el username desde la sesión almacenada en MongoDB."""
    session = await db.sesiones.find_one({"token": token}, {"_id": 0, "username": 1})
    return session["username"] if session else "unknown"


@router.post("/Listado", response_model=List[ClientListItem])
async def list_clients(payload: ClientListRequest, token: str = Depends(_bearer_header)):
    http = get_http_client()

    try:
        response = await http.post(
            "/api/Cliente/Listado",
            json=payload.model_dump(exclude_none=True),
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception:
        logger.exception("Error listando clientes")
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al listar clientes.")

    return response.json()


@router.get("/Obtener/{client_id}", response_model=ClientDetail)
async def get_client(client_id: str, token: str = Depends(_bearer_header)):
    http = get_http_client()

    try:
        response = await http.get(
            f"/api/Cliente/Obtener/{client_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception:
        logger.exception("Error obteniendo cliente %s", client_id)
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener el cliente.")

    return response.json()


@router.post("/Crear")
async def create_client(payload: ClientCreateRequest, token: str = Depends(_bearer_header)):
    http = get_http_client()
    db = get_db()
    username = await _get_username_from_token(token, db)

    try:
        response = await http.post(
            "/api/Cliente/Crear",
            json=payload.model_dump(exclude_none=True),
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception:
        logger.exception("Error creando cliente")
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    result_data = response.json() if response.content else {}
    cliente_id = str(result_data.get("id", "unknown"))
    await _audit(db, "CREAR", username, cliente_id, response.status_code)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=result_data if response.content else "Error al crear el cliente.",
        )

    return {"message": "Cliente creado correctamente.", "data": result_data}


@router.post("/Actualizar")
async def update_client(payload: ClientUpdateRequest, token: str = Depends(_bearer_header)):
    http = get_http_client()
    db = get_db()
    username = await _get_username_from_token(token, db)

    try:
        response = await http.post(
            "/api/Cliente/Actualizar",
            json=payload.model_dump(exclude_none=True),
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception:
        logger.exception("Error actualizando cliente %s", payload.id)
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    await _audit(db, "ACTUALIZAR", username, payload.id, response.status_code)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json() if response.content else "Error al actualizar el cliente.",
        )

    return {"message": "Cliente actualizado correctamente."}


@router.delete("/Eliminar/{client_id}")
async def delete_client(client_id: str, token: str = Depends(_bearer_header)):
    http = get_http_client()
    db = get_db()
    username = await _get_username_from_token(token, db)

    try:
        response = await http.delete(
            f"/api/Cliente/Eliminar/{client_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    except Exception:
        logger.exception("Error eliminando cliente %s", client_id)
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    await _audit(db, "ELIMINAR", username, client_id, response.status_code)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al eliminar el cliente.",
        )

    return {"message": "Cliente eliminado correctamente."}
