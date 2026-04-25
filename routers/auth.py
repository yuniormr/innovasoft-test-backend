from fastapi import APIRouter

import services.auth as auth_service
from core.dependencies import HttpClient, Database, BearerToken
from schemas.auth import LoginRequest, RegisterRequest, LoginResponse, RegisterResponse

router = APIRouter(prefix="/api/Authenticate", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, http: HttpClient, db: Database):
    return await auth_service.login(payload, http, db)


@router.post("/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest, http: HttpClient):
    return await auth_service.register(payload, http)


@router.post("/logout")
async def logout(token: BearerToken, db: Database):
    return await auth_service.logout(token, db)

