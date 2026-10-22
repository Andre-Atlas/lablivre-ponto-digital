"""Integração US2: gestão do catálogo de LOs (CRUD + RBAC + preservação de histórico)."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.domain.enums import RoleAdmin, TipoUsuario
from app.main import app
from tests.integration.lo_fixtures import auth, cleanup, seed_config, seed_lo, seed_user


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


@pytest_asyncio.fixture
async def env() -> AsyncGenerator[dict, None]:
    await seed_config()
    admin = await seed_user(
        tipo=TipoUsuario.STAFF, role=RoleAdmin.ADMIN, turma="Turma 1", nome="Admin"
    )
    mentor = await seed_user(
        tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 1", nome="Mentor"
    )
    aluno = await seed_user(
        tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma 1", nome="Aluno"
    )
    created_los: list = []
    yield {"admin": admin, "mentor": mentor, "aluno": aluno, "created_los": created_los}
    await cleanup([admin, mentor, aluno], created_los)


@pytest.mark.asyncio
async def test_admin_create_list_and_rbac(env: dict) -> None:
    async with _client() as c:
        created = await c.post(
            "/api/v1/admin/los", json={"numero": 10, "nome": "LO Dez"}, headers=auth(env["admin"])
        )
        assert created.status_code == 201, created.text
        env["created_los"].append(created.json()["id"])

        listed = await c.get("/api/v1/admin/los", headers=auth(env["mentor"]))
        assert listed.status_code == 200 and any(x["numero"] == 10 for x in listed.json())

        dup = await c.post(
            "/api/v1/admin/los", json={"numero": 10, "nome": "Dup"}, headers=auth(env["admin"])
        )
        mentor_create = await c.post(
            "/api/v1/admin/los", json={"numero": 11, "nome": "x"}, headers=auth(env["mentor"])
        )
        student_create = await c.post(
            "/api/v1/admin/los", json={"numero": 12, "nome": "y"}, headers=auth(env["aluno"])
        )
    assert dup.status_code == 400
    assert mentor_create.status_code == 403
    assert student_create.status_code == 403


@pytest.mark.asyncio
async def test_deactivate_hides_but_preserves_history(env: dict) -> None:
    # seed an LO and an evaluation referencing it, then deactivate the LO
    lo = await seed_lo(20, "LO Vinte")
    env["created_los"].append(str(lo))
    async with _client() as c:
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["aluno"]), "semana": 2, "niveis": {str(lo): 3}},
            headers=auth(env["mentor"]),
        )
        deactivate = await c.put(
            f"/api/v1/admin/los/{lo}", json={"ativo": False}, headers=auth(env["admin"])
        )
        active = await c.get("/api/v1/admin/los", headers=auth(env["mentor"]))
        incl = await c.get("/api/v1/admin/los?incluir_inativos=true", headers=auth(env["mentor"]))
        ev = await c.get(
            f"/api/v1/admin/avaliacoes?user_id={env['aluno']}&semana=2", headers=auth(env["mentor"])
        )
    assert deactivate.status_code == 200 and deactivate.json()["ativo"] is False
    assert all(x["id"] != str(lo) for x in active.json())  # hidden from active list
    assert any(x["id"] == str(lo) for x in incl.json())  # visible with incluir_inativos
    assert any(
        n["lo_id"] == str(lo) and n["nivel"] == 3 for n in ev.json()["niveis"]
    )  # history intact
