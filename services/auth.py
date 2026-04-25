import logging
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.http_utils import proxy_request
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse

logger = logging.getLogger(__name__)


async def login(
    payload: LoginRequest,
    http: httpx.AsyncClient,
    db: AsyncIOMotorDatabase,
) -> LoginResponse:
    response = await proxy_request(
        http.post(
            "/api/Authenticate/login",
            json={"username": payload.username, "password": payload.password},
        )
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json() if response.content else "Credenciales inválidas.",
        )

    data = response.json()
    await db.sesiones.insert_one({
        "token": data["token"],
        "userid": data["userid"],
        "username": data["username"],
        "login_timestamp": datetime.now(timezone.utc),
    })
    logger.info("Sesión creada para usuario: %s", data["username"])
    return LoginResponse(**data)


async def register(
    payload: RegisterRequest,
    http: httpx.AsyncClient,
) -> RegisterResponse:
    response = await proxy_request(
        http.post(
            "/api/Authenticate/register",
            json={
                "username": payload.username,
                "email": str(payload.email),
                "password": payload.password,
            },
        )
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json() if response.content else "Error al registrar el usuario.",
        )

    return RegisterResponse(**response.json())


async def logout(token: str, db: AsyncIOMotorDatabase) -> dict:
    result = await db.sesiones.delete_one({"token": token})
    if result.deleted_count == 0:
        logger.info("Logout: sesión no encontrada en MongoDB (token ya expirado o inválido).")
    return {"message": "Sesión cerrada correctamente."}
