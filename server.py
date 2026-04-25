import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import close_mongo_client
from core.httpx_client import close_http_client
from routers import auth, clients, interests

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_http_client()
    close_mongo_client()


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Clientes BFF",
    description="Backend for Frontend — intermedia entre React y la API de Innovasoft.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
