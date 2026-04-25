import logging
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.http_utils import proxy_request
from schemas.clients import (
    ClientCreateRequest,
    ClientDetail,
    ClientListItem,
    ClientListRequest,
    ClientMutationResponse,
    ClientUpdateRequest,
)

logger = logging.getLogger(__name__)


# ── Helpers internos ──────────────────────────────────────────────────────────

async def get_username_from_token(token: str, db: AsyncIOMotorDatabase) -> str:
    """Recupera el username desde la sesión almacenada en MongoDB."""
    session = await db.sesiones.find_one({"token": token}, {"_id": 0, "username": 1})
    return session["username"] if session else "unknown"


async def audit(
    db: AsyncIOMotorDatabase,
    accion: str,
    usuario: str,
    cliente_id: str,
    resultado: int,
) -> None:
    """Registra una operación CRUD en la colección `operaciones`."""
    await db.operaciones.insert_one({
        "accion": accion,
        "usuario": usuario,
        "cliente_id": cliente_id,
        "timestamp": datetime.now(timezone.utc),
        "resultado": resultado,
    })


# ── Operaciones de negocio ────────────────────────────────────────────────────

async def list_clients(
    payload: ClientListRequest,
    token: str,
    http: httpx.AsyncClient,
) -> list[ClientListItem]:
    response = await proxy_request(
        http.post(
            "/api/Cliente/Listado",
            json=payload.model_dump(exclude_none=True),
            headers={"Authorization": f"Bearer {token}"},
        )
    )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al listar clientes.")
    return [ClientListItem(**item) for item in response.json()]


async def get_client(
    client_id: str,
    token: str,
    http: httpx.AsyncClient,
) -> ClientDetail:
    response = await proxy_request(
        http.get(
            f"/api/Cliente/Obtener/{client_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener el cliente.")
    return ClientDetail(**response.json())


async def create_client(
    payload: ClientCreateRequest,
    token: str,
    http: httpx.AsyncClient,
    db: AsyncIOMotorDatabase,
) -> ClientMutationResponse:
    username = await get_username_from_token(token, db)
    response = await proxy_request(
        http.post(
            "/api/Cliente/Crear",
            json=payload.model_dump(exclude_none=True),
            headers={"Authorization": f"Bearer {token}"},
        )
    )
    result_data = response.json() if response.content else {}
    cliente_id = str(result_data.get("id", "unknown"))
    await audit(db, "CREAR", username, cliente_id, response.status_code)

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=response.status_code,
            detail=result_data if response.content else "Error al crear el cliente.",
        )
    return ClientMutationResponse(message="Cliente creado correctamente.", data=result_data)


async def update_client(
    payload: ClientUpdateRequest,
    token: str,
    http: httpx.AsyncClient,
    db: AsyncIOMotorDatabase,
) -> ClientMutationResponse:
    username = await get_username_from_token(token, db)
    response = await proxy_request(
        http.post(
            "/api/Cliente/Actualizar",
            json=payload.model_dump(exclude_none=True),
            headers={"Authorization": f"Bearer {token}"},
        )
    )
    await audit(db, "ACTUALIZAR", username, payload.id, response.status_code)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json() if response.content else "Error al actualizar el cliente.",
        )
    return ClientMutationResponse(message="Cliente actualizado correctamente.")


async def delete_client(
    client_id: str,
    token: str,
    http: httpx.AsyncClient,
    db: AsyncIOMotorDatabase,
) -> ClientMutationResponse:
    username = await get_username_from_token(token, db)
    response = await proxy_request(
        http.delete(
            f"/api/Cliente/Eliminar/{client_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    )
    await audit(db, "ELIMINAR", username, client_id, response.status_code)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error al eliminar el cliente.",
        )
    return ClientMutationResponse(message="Cliente eliminado correctamente.")
