"""Integração US3: dashboard da turma/semana (avaliados/pendentes, por mentor, heatmap, regressões)."""

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
    mentor = await seed_user(
        tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 1", nome="Mentor A"
    )
    mentor2 = await seed_user(
        tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 1", nome="Mentor B"
    )
    a1 = await seed_user(
        tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma 1", nome="Aluno 1"
    )
    a2 = await seed_user(
        tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma 1", nome="Aluno 2"
    )
    a3 = await seed_user(
        tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma 1", nome="Aluno 3"
    )
    lo1 = await seed_lo(1, "LO 1")
    lo2 = await seed_lo(2, "LO 2")
    yield {
        "mentor": mentor,
        "mentor2": mentor2,
        "a1": a1,
        "a2": a2,
        "a3": a3,
        "lo1": lo1,
        "lo2": lo2,
    }
    await cleanup([mentor, mentor2, a1, a2, a3], [lo1, lo2])


@pytest.mark.asyncio
async def test_dashboard_counts_heatmap_regressions(env: dict) -> None:
    async with _client() as c:
        m = auth(env["mentor"])
        m2 = auth(env["mentor2"])
        # a1: week2 lo1=3 (prior), week3 lo1=2 (regression) + lo2=4, by mentor A
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["a1"]), "semana": 2, "niveis": {str(env["lo1"]): 3}},
            headers=m,
        )
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={
                "user_id": str(env["a1"]),
                "semana": 3,
                "niveis": {str(env["lo1"]): 2, str(env["lo2"]): 4},
            },
            headers=m,
        )
        # a2: week3 lo1=3 by mentor B
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["a2"]), "semana": 3, "niveis": {str(env["lo1"]): 3}},
            headers=m2,
        )
        # a3: left pending
        dash = await c.get("/api/v1/admin/avaliacoes/dashboard?turma=Turma%201&semana=3", headers=m)
    assert dash.status_code == 200, dash.text
    d = dash.json()
    assert d["total_alunos"] == 3
    assert d["avaliados"] == 2
    assert [p["nome"] for p in d["pendentes"]] == ["Aluno 3"]
    por_mentor = {m_["mentor_nome"]: m_["alunos_avaliados"] for m_ in d["por_mentor"]}
    assert por_mentor.get("Mentor A") == 1 and por_mentor.get("Mentor B") == 1
    # heatmap lo1: a1=2, a2=3 → counts [0,1,1,0]
    hm = {h["numero"]: h["contagem"] for h in d["heatmap"]}
    assert hm[1] == [0, 1, 1, 0]
    assert hm[2] == [0, 0, 0, 1]
    # regression: a1 lo1 dropped 3 -> 2
    regs = [
        (r["nome"], r["numero"], r["nivel_atual"], r["nivel_anterior"]) for r in d["regressoes"]
    ]
    assert ("Aluno 1", 1, 2, 3) in regs


@pytest.mark.asyncio
async def test_dashboard_rbac_student_forbidden(env: dict) -> None:
    async with _client() as c:
        r = await c.get(
            "/api/v1/admin/avaliacoes/dashboard?turma=Turma%201&semana=3", headers=auth(env["a1"])
        )
    assert r.status_code == 403
