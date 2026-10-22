import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    router_admin,
    router_auth,
    router_certificates,
    router_evaluations,
    router_frequencia,
)
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    # Inicialização do banco de dados (se necessário)
    yield
    # Limpeza


app = FastAPI(title="Ponto Digital API", version=settings.APP_VERSION, lifespan=lifespan)

# CORS — em produção defina CORS_ORIGINS (origens separadas por vírgula);
# sem a variável, libera tudo (conveniente em dev).
_cors_env = os.getenv("CORS_ORIGINS", "").strip()
_allow_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_auth.router, prefix="/api/v1")
app.include_router(router_admin.router, prefix="/api/v1")
app.include_router(router_certificates.router, prefix="/api/v1")
app.include_router(router_evaluations.router, prefix="/api/v1")
app.include_router(router_frequencia.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health() -> Any:
    return {"status": "healthy", "version": settings.APP_VERSION}
