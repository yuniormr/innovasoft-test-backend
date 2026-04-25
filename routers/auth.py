from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from datetime import datetime, timezone
import logging

from core.httpx_client import get_http_client
from core.database import get_db
from schemas.auth import LoginRequest, RegisterRequest, LoginResponse, RegisterResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/Authenticate", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    """
    Autentica contra la API de Innovasoft, persiste la sesión en MongoDB
    y retorna el token JWT al frontend.
    """
    client = get_http_client()
    db = get_db()

    try:
        response = await client.post(
            "/api/Authenticate/login",
            json={"username": payload.username, "password": payload.password},
        )
    except Exception as exc:
        logger.exception("Error conectando con la API de Innovasoft")
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json() if response.content else "Credenciales inválidas.",
        )

    data = response.json()

    # Persistir sesión en MongoDB
    session_doc = {
        "token": data["token"],
        "userid": data["userid"],
        "username": data["username"],
        "login_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.sesiones.insert_one(session_doc)
    logger.info("Sesión creada para usuario: %s", data["username"])

    return LoginResponse(**data)


@router.post("/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest):
    """
    Registra un nuevo usuario en la API de Innovasoft.
    La validación de password se hace en el schema RegisterRequest.
    """
    client = get_http_client()

    try:
        response = await client.post(
            "/api/Authenticate/register",
            json={
                "username": payload.username,
                "email": str(payload.email),
                "password": payload.password,
            },
        )
    except Exception:
        logger.exception("Error conectando con la API de Innovasoft durante el registro")
        raise HTTPException(status_code=502, detail="Error al conectar con el servidor externo.")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json() if response.content else "Error al registrar el usuario.",
        )

    return RegisterResponse(**response.json())


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(default=None)):
    """
    Elimina el documento de sesión en MongoDB usando el token del header Authorization.
    """
    db = get_db()

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido.")

    token = authorization.removeprefix("Bearer ").strip()
    result = await db.sesiones.delete_one({"token": token})

    if result.deleted_count == 0:
        # La sesión ya no existe — se acepta igual (idempotente)
        logger.info("Logout: sesión no encontrada en MongoDB (token ya expirado o inválido).")

    return {"message": "Sesión cerrada correctamente."}
