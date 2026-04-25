import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

from core.config import settings
from routers import auth, clients, interests

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.INNOVASOFT_API_BASE,
        timeout=30.0,
        follow_redirects=True,
    )
    app.state.mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    app.state.db = app.state.mongo_client[settings.DB_NAME]
    yield
    await app.state.http_client.aclose()
    app.state.mongo_client.close()


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Clientes BFF",
    description="Backend for Frontend — intermedia entre React y la API de Innovasoft.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(interests.router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Bienvenido!!!"}


# ── OpenAPI con Bearer auth ───────────────────────────────────────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Aplica el esquema a todos los endpoints excepto login, register y health
    public_paths = {"/api/auth/login", "/api/auth/register", "/health", "/"}
    for path, methods in schema.get("paths", {}).items():
        if path in public_paths:
            continue
        for method in methods.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]
