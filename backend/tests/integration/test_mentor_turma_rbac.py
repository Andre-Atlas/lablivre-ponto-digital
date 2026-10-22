"""Integração: RBAC mentor–turma + regressão FR-010 (aluno = 1 turma)."""
import json
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
    async with async_session_maker() as s:
        await s.execute(ConfigModel.__table__.delete().where(ConfigModel.chave == "turmas"))
        s.add(ConfigModel(id=uuid.uuid4(), chave="turmas", valor=json.dumps(list(nomes)), atualizado_em=datetime.now(UTC)))
        await s.commit()


@pytest_asyncio.fixture
async def ctx() -> AsyncGenerator[dict, None]:
    await _seed_turmas("Turma A", "Turma B")
    admin = await seed_user(tipo=TipoUsuario.STAFF, role=RoleAdmin.ADMIN, turma="Turma A", nome="Admin")
    mentor = await seed_user(tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma A", nome="Mentor")
    a = await seed_user(tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma A", nome="AlunoA")
    yield {"admin": admin, "mentor": mentor, "a": a}
    await cleanup([admin, mentor, a], [])


@pytest.mark.asyncio
async def test_escopo_mentor_por_turma(ctx: dict) -> None:
    async with _client() as c:
        # admin atribui "Turma A" ao mentor
        r = await c.put(f"/api/v1/admin/mentores/{ctx['mentor']}/turmas", headers=auth(ctx["admin"]), json={"turmas": ["Turma A"]})
        assert r.status_code == 200, r.text
        assert r.json() == ["Turma A"]

        g = await c.get(f"/api/v1/admin/mentores/{ctx['mentor']}/turmas", headers=auth(ctx["admin"]))
        assert g.json() == ["Turma A"]

        Hm = auth(ctx["mentor"])
        # mentor vê só Turma A em /frequencia/turmas
        mt = await c.get("/api/v1/frequencia/turmas", headers=Hm)
        assert mt.json() == ["Turma A"]
        # admin vê todas
        at = await c.get("/api/v1/frequencia/turmas", headers=auth(ctx["admin"]))
        assert set(at.json()) == {"Turma A", "Turma B"}

        # mentor pode GET sua turma, 403 em outra
        ok = await c.get("/api/v1/frequencia", headers=Hm, params={"turma": "Turma A", "data": "2026-10-15", "turno": "MANHA"})
        assert ok.status_code == 200
        forbidden = await c.get("/api/v1/frequencia", headers=Hm, params={"turma": "Turma B", "data": "2026-10-15", "turno": "MANHA"})
        assert forbidden.status_code == 403

        # admin acessa qualquer turma
        adm = await c.get("/api/v1/frequencia", headers=auth(ctx["admin"]), params={"turma": "Turma B", "data": "2026-10-15", "turno": "MANHA"})
        assert adm.status_code == 200


@pytest.mark.asyncio
async def test_fr010_aluno_exige_turma_cadastrada(ctx: dict) -> None:
    H = auth(ctx["admin"])
    async with _client() as c:
        # turma não cadastrada → 400
        bad = await c.post("/api/v1/admin/alunos", headers=H, json={"nome": "X", "email": f"x_{uuid.uuid4().hex[:6]}@t.lab", "turma_ou_equipe": "Turma Z"})
        assert bad.status_code == 400
        # turma cadastrada → 201
        ok = await c.post("/api/v1/admin/alunos", headers=H, json={"nome": "Y", "email": f"y_{uuid.uuid4().hex[:6]}@t.lab", "turma_ou_equipe": "Turma A"})
        assert ok.status_code == 201
