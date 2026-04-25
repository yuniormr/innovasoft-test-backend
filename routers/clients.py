from typing import List

from fastapi import APIRouter

import services.clients as clients_service
from core.dependencies import HttpClient, Database, BearerToken
from schemas.clients import (
    ClientListRequest,
    ClientListItem,
    ClientDetail,
    ClientCreateRequest,
    ClientUpdateRequest,
    ClientMutationResponse,
)

router = APIRouter(prefix="/api/Cliente", tags=["Clientes"])


@router.post("/Listado", response_model=List[ClientListItem])
async def list_clients(payload: ClientListRequest, token: BearerToken, http: HttpClient):
    return await clients_service.list_clients(payload, token, http)


@router.get("/Obtener/{client_id}", response_model=ClientDetail)
async def get_client(client_id: str, token: BearerToken, http: HttpClient):
    return await clients_service.get_client(client_id, token, http)


@router.post("/Crear", response_model=ClientMutationResponse, status_code=201)
async def create_client(payload: ClientCreateRequest, token: BearerToken, http: HttpClient, db: Database):
    return await clients_service.create_client(payload, token, http, db)


@router.post("/Actualizar", response_model=ClientMutationResponse)
async def update_client(payload: ClientUpdateRequest, token: BearerToken, http: HttpClient, db: Database):
    return await clients_service.update_client(payload, token, http, db)


@router.delete("/Eliminar/{client_id}", response_model=ClientMutationResponse)
async def delete_client(client_id: str, token: BearerToken, http: HttpClient, db: Database):
    return await clients_service.delete_client(client_id, token, http, db)

