"""Integração: só mentores autenticam; aluno não loga; autofrequência removida."""
import uuid
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import User as UserModel
from app.domain.enums import RoleAdmin, TipoUsuario
from app.main import app
from app.utils.security import get_password_hash


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def _seed(tipo: TipoUsuario, role: RoleAdmin, email: str, senha: str) -> None:
    uid = uuid.uuid4()
    now = datetime.now(UTC)
    async with async_session_maker() as s:
        s.add(
            UserModel(
                id=uid, email=email, nome="U", tipo=tipo, role=role, turma_ou_equipe="T",
                oauth_provider="m", oauth_sub=str(uid), senha_hash=get_password_hash(senha),
                ativo=True, admin_aprovado=True, criado_em=now, atualizado_em=now,
            )
        )
        await s.commit()


@pytest.mark.asyncio
async def test_mentor_loga_aluno_nao() -> None:
    await _seed(TipoUsuario.STAFF, RoleAdmin.ADMIN, "mentor_x@t.com", "senha123")
    await _seed(TipoUsuario.ALUNO, RoleAdmin.NONE, "aluno_x@t.com", "senha123")
    async with _client() as c:
        m = await c.post("/api/v1/auth/login", json={"email": "mentor_x@t.com", "senha": "senha123"})
        assert m.status_code == 200, m.text
        assert m.json()["tipo"] == "ADMIN"

        a = await c.post("/api/v1/auth/login", json={"email": "aluno_x@t.com", "senha": "senha123"})
        assert a.status_code == 403


@pytest.mark.asyncio
async def test_autofrequencia_e_registro_removidos() -> None:
    async with _client() as c:
        # rota de auto-check-in não existe mais
        chk = await c.post("/api/v1/checkin/", json={"lat": 0, "lng": 0})
        assert chk.status_code == 404
        # autorregistro de aluno não existe mais
        reg = await c.post(
            "/api/v1/auth/register",
            json={"nome": "x", "email": "y@t.com", "senha": "z", "turma": "T", "numero_maquina": 1},
        )
        assert reg.status_code == 404
