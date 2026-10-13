"""Integração US1: registrar avaliação semanal + pré-preenchimento + escopo + co-avaliação."""

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
    await seed_config(data_inicio="2026-01-05", num_semanas=12)
    mentor = await seed_user(
        tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 1", nome="Mentor A"
    )
    mentor2 = await seed_user(
        tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 1", nome="Mentor B"
    )
    outro = await seed_user(
        tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 2", nome="Mentor C"
    )
    aluno = await seed_user(
        tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma 1", nome="Aluno X"
    )
    lo1 = await seed_lo(1, "Pensamento computacional")
    lo2 = await seed_lo(2, "Comunicação")
    yield {
        "mentor": mentor,
        "mentor2": mentor2,
        "outro": outro,
        "aluno": aluno,
        "lo1": lo1,
        "lo2": lo2,
    }
    await cleanup([mentor, mentor2, outro, aluno], [lo1, lo2])


@pytest.mark.asyncio
async def test_submit_and_get_roundtrip(env: dict) -> None:
    body = {
        "user_id": str(env["aluno"]),
        "semana": 3,
        "niveis": {str(env["lo1"]): 2, str(env["lo2"]): 3},
        "comentario": "Boa evolução",
    }
    async with _client() as c:
        r = await c.post("/api/v1/admin/avaliacoes", json=body, headers=auth(env["mentor"]))
        assert r.status_code == 200, r.text
        got = await c.get(
            f"/api/v1/admin/avaliacoes?user_id={env['aluno']}&semana=3", headers=auth(env["mentor"])
        )
    assert got.status_code == 200
    niveis = {n["lo_id"]: n["nivel"] for n in got.json()["niveis"]}
    assert niveis == {str(env["lo1"]): 2, str(env["lo2"]): 3}
    assert any(c_["texto"] == "Boa evolução" for c_ in got.json()["comentarios"])


@pytest.mark.asyncio
async def test_prefill_reflects_prior_week(env: dict) -> None:
    async with _client() as c:
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={
                "user_id": str(env["aluno"]),
                "semana": 3,
                "niveis": {str(env["lo1"]): 2, str(env["lo2"]): 3},
            },
            headers=auth(env["mentor"]),
        )
        pf = await c.get(
            f"/api/v1/admin/avaliacoes/prefill?user_id={env['aluno']}&semana=4",
            headers=auth(env["mentor"]),
        )
    assert pf.status_code == 200
    assert pf.json()["niveis"] == {str(env["lo1"]): 2, str(env["lo2"]): 3}


@pytest.mark.asyncio
async def test_validation_errors(env: dict) -> None:
    async with _client() as c:
        bad_level = await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["aluno"]), "semana": 3, "niveis": {str(env["lo1"]): 5}},
            headers=auth(env["mentor"]),
        )
        unknown_lo = await c.post(
            "/api/v1/admin/avaliacoes",
            json={
                "user_id": str(env["aluno"]),
                "semana": 3,
                "niveis": {"00000000-0000-0000-0000-000000000000": 2},
            },
            headers=auth(env["mentor"]),
        )
        bad_week = await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["aluno"]), "semana": 99, "niveis": {str(env["lo1"]): 2}},
            headers=auth(env["mentor"]),
        )
    assert bad_level.status_code == 400
    assert unknown_lo.status_code == 400
    assert bad_week.status_code == 400


@pytest.mark.asyncio
async def test_turma_scoping_forbidden(env: dict) -> None:
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["aluno"]), "semana": 3, "niveis": {str(env["lo1"]): 2}},
            headers=auth(env["outro"]),
        )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_co_evaluation_last_level_wins_both_comments(env: dict) -> None:
    async with _client() as c:
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={
                "user_id": str(env["aluno"]),
                "semana": 3,
                "niveis": {str(env["lo1"]): 2},
                "comentario": "A: começando",
            },
            headers=auth(env["mentor"]),
        )
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={
                "user_id": str(env["aluno"]),
                "semana": 3,
                "niveis": {str(env["lo1"]): 4},
                "comentario": "B: avançou",
            },
            headers=auth(env["mentor2"]),
        )
        got = await c.get(
            f"/api/v1/admin/avaliacoes?user_id={env['aluno']}&semana=3", headers=auth(env["mentor"])
        )
    data = got.json()
    niveis = {n["lo_id"]: n["nivel"] for n in data["niveis"]}
    assert niveis[str(env["lo1"])] == 4  # last write wins
    textos = {c_["texto"] for c_ in data["comentarios"]}
    assert textos == {"A: começando", "B: avançou"}  # both kept


@pytest.mark.asyncio
async def test_rbac_and_not_found(env: dict) -> None:
    async with _client() as c:
        student_tok = await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["aluno"]), "semana": 3, "niveis": {str(env["lo1"]): 2}},
            headers=auth(env["aluno"]),
        )
        no_tok = await c.post(
            "/api/v1/admin/avaliacoes",
            json={"user_id": str(env["aluno"]), "semana": 3, "niveis": {str(env["lo1"]): 2}},
        )
        not_found = await c.post(
            "/api/v1/admin/avaliacoes",
            json={
                "user_id": "11111111-1111-1111-1111-111111111111",
                "semana": 3,
                "niveis": {str(env["lo1"]): 2},
            },
            headers=auth(env["mentor"]),
        )
    assert student_tok.status_code == 403
    assert no_tok.status_code == 401
    assert not_found.status_code == 404
