from typing import List

from fastapi import APIRouter, Depends

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

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.get("/", response_model=List[ClientListItem])
async def list_clients(token: BearerToken, http: HttpClient, filters: ClientListRequest = Depends()):
    return await clients_service.list_clients(filters, token, http)


@router.get("/{client_id}", response_model=ClientDetail)
async def get_client(client_id: str, token: BearerToken, http: HttpClient):
    return await clients_service.get_client(client_id, token, http)


@router.post("/", response_model=ClientMutationResponse, status_code=201)
async def create_client(payload: ClientCreateRequest, token: BearerToken, http: HttpClient, db: Database):
    return await clients_service.create_client(payload, token, http, db)


@router.put("/{client_id}", response_model=ClientMutationResponse)
async def update_client(client_id: str, payload: ClientUpdateRequest, token: BearerToken, http: HttpClient, db: Database):
    return await clients_service.update_client(client_id, payload, token, http, db)


@router.delete("/{client_id}", response_model=ClientMutationResponse)
async def delete_client(client_id: str, token: BearerToken, http: HttpClient, db: Database):
    return await clients_service.delete_client(client_id, token, http, db)

    return await clients_service.create_client(payload, token, http, db)


# @router.post("/Actualizar", response_model=ClientMutationResponse)
# async def update_client(payload: ClientUpdateRequest, token: BearerToken, http: HttpClient, db: Database):
#     return await clients_service.update_client(payload, token, http, db)


# @router.delete("/Eliminar/{client_id}", response_model=ClientMutationResponse)
# async def delete_client(client_id: str, token: BearerToken, http: HttpClient, db: Database):
#     return await clients_service.delete_client(client_id, token, http, db)

