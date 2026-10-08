from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1 import router_auth
from app.api.v1 import router_checkin
from app.api.v1 import router_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
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
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}
