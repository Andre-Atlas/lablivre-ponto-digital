from contextlib import asynccontextmanager

from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router_admin, router_auth, router_checkin
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    # Inicialização do banco de dados (se necessário)
    yield
    # Limpeza


app = FastAPI(title="Ponto Digital API", version=settings.APP_VERSION, lifespan=lifespan)

# CORS (allow all in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_auth.router, prefix="/api/v1")
app.include_router(router_checkin.router, prefix="/api/v1")
app.include_router(router_admin.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health() -> Any:
    return {"status": "healthy", "version": settings.APP_VERSION}
