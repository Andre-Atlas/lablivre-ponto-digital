"""Integração: registro de aluno (ALUNO) como registro administrado (gap do pivô admin)."""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import Config as ConfigModel
from app.domain.enums import RoleAdmin, TipoUsuario
from app.main import app
from tests.integration.lo_fixtures import auth, cleanup, seed_user


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def _seed_turmas(*nomes: str) -> None:
    import json

    async with async_session_maker() as s:
        await s.execute(ConfigModel.__table__.delete().where(ConfigModel.chave == "turmas"))
        s.add(
            ConfigModel(
                id=uuid.uuid4(),
                chave="turmas",
                valor=json.dumps(list(nomes)),
                atualizado_em=datetime.now(UTC),
            )
        )
        await s.commit()


@pytest_asyncio.fixture
async def actors() -> AsyncGenerator[dict, None]:
    await _seed_turmas("Turma 1")
    admin = await seed_user(tipo=TipoUsuario.STAFF, role=RoleAdmin.ADMIN, turma="Turma 1", nome="Admin")
    staff = await seed_user(tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 1", nome="Staff")
    yield {"admin": admin, "staff": staff}
    await cleanup([admin, staff], [])


@pytest.mark.asyncio
async def test_admin_registers_aluno(actors: dict) -> None:
    email = f"aluno_{uuid.uuid4().hex[:8]}@turma.lab"
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/alunos",
            json={"nome": "Novo Aluno", "email": email, "turma_ou_equipe": "Turma 1"},
            headers=auth(actors["admin"]),
        )
        assert r.status_code == 201, r.text
        assert r.json()["tipo"] == "ALUNO"
        listed = await c.get("/api/v1/admin/usuarios", headers=auth(actors["admin"]))
    assert any(u["email"] == email and u["tipo"] == "ALUNO" for u in listed.json())


@pytest.mark.asyncio
async def test_register_aluno_rbac_and_validation(actors: dict) -> None:
    async with _client() as c:
        # non-admin STAFF cannot register
        forbidden = await c.post(
            "/api/v1/admin/alunos",
            json={"nome": "X", "email": f"x_{uuid.uuid4().hex[:6]}@t.lab", "turma_ou_equipe": "Turma 1"},
            headers=auth(actors["staff"]),
        )
        # missing turma
        bad = await c.post(
            "/api/v1/admin/alunos",
            json={"nome": "Y", "email": f"y_{uuid.uuid4().hex[:6]}@t.lab", "turma_ou_equipe": ""},
            headers=auth(actors["admin"]),
        )
        # duplicate email
        dupe_email = f"dupe_{uuid.uuid4().hex[:6]}@t.lab"
        first = await c.post(
            "/api/v1/admin/alunos",
            json={"nome": "Z", "email": dupe_email, "turma_ou_equipe": "Turma 1"},
            headers=auth(actors["admin"]),
        )
        dup = await c.post(
            "/api/v1/admin/alunos",
            json={"nome": "Z2", "email": dupe_email, "turma_ou_equipe": "Turma 1"},
            headers=auth(actors["admin"]),
        )
    assert forbidden.status_code == 403
    assert bad.status_code == 400
    assert first.status_code == 201
    assert dup.status_code == 409
