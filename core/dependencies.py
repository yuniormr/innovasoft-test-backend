from typing import Annotated

import httpx
from fastapi import Depends, Header, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db


def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorización requerido.")
    return authorization.removeprefix("Bearer ").strip()


HttpClient = Annotated[httpx.AsyncClient, Depends(get_http_client)]
Database = Annotated[AsyncIOMotorDatabase, Depends(get_db)]
BearerToken = Annotated[str, Depends(get_bearer_token)]
