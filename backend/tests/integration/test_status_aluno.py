"""Integração: status do aluno (Ativo/Desligado) e seus efeitos."""
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.domain.enums import RoleAdmin, TipoUsuario
from app.main import app
from tests.integration.lo_fixtures import auth, cleanup, seed_user

TURMA = "Turma A"


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


@pytest_asyncio.fixture
async def ctx() -> AsyncGenerator[dict, None]:
    admin = await seed_user(tipo=TipoUsuario.STAFF, role=RoleAdmin.ADMIN, turma=TURMA, nome="Admin")
    aluno = await seed_user(tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma=TURMA, nome="AlunoX")
    yield {"admin": admin, "aluno": aluno}
    await cleanup([admin, aluno], [])


async def _freq_alunos(c: AsyncClient, H: dict) -> set[str]:
    g = await c.get("/api/v1/frequencia", headers=H, params={"turma": TURMA, "data": "2026-10-15", "turno": "MANHA"})
    assert g.status_code == 200, g.text
    return {row["aluno_nome"] for row in g.json()}


@pytest.mark.asyncio
async def test_desligar_remove_das_listas_e_mantem_historico(ctx: dict) -> None:
    H = auth(ctx["admin"])
    async with _client() as c:
        # começa Ativo → aparece na lista de frequência
        assert "AlunoX" in await _freq_alunos(c, H)

        # desligar
        r = await c.put(f"/api/v1/admin/alunos/{ctx['aluno']}/status", headers=H, json={"status": "DESLIGADO"})
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "DESLIGADO"

        # some da lista ativa de frequência
        assert "AlunoX" not in await _freq_alunos(c, H)

        # continua no filtro de desligados e no export histórico
        listed = await c.get("/api/v1/admin/usuarios", headers=H, params={"status": "DESLIGADO"})
        assert any(u["nome"] == "AlunoX" for u in listed.json())
        exp = await c.get("/api/v1/admin/export/usuarios", headers=H)
        assert "AlunoX" in exp.text and "DESLIGADO" in exp.text

        # reativar → volta às listas ativas
        back = await c.put(f"/api/v1/admin/alunos/{ctx['aluno']}/status", headers=H, json={"status": "ATIVO"})
        assert back.status_code == 200
        assert "AlunoX" in await _freq_alunos(c, H)


@pytest.mark.asyncio
async def test_status_invalido_400(ctx: dict) -> None:
    H = auth(ctx["admin"])
    async with _client() as c:
        r = await c.put(f"/api/v1/admin/alunos/{ctx['aluno']}/status", headers=H, json={"status": "XPTO"})
        assert r.status_code == 400
