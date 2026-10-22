"""Integração: lançamento de frequência pelo mentor + atestado por turno."""
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.domain.enums import RoleAdmin, TipoUsuario
from app.main import app
from tests.integration.lo_fixtures import auth, cleanup, seed_user

DATA = "2026-10-15"
TURMA = "Turma A"
PDF = {"documento": ("a.pdf", b"%PDF-1.4 teste", "application/pdf")}


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


@pytest_asyncio.fixture
async def ctx() -> AsyncGenerator[dict, None]:
    mentor = await seed_user(tipo=TipoUsuario.STAFF, role=RoleAdmin.ADMIN, turma=TURMA, nome="Mentor")
    a1 = await seed_user(tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma=TURMA, nome="Aluno1")
    a2 = await seed_user(tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma=TURMA, nome="Aluno2")
    yield {"mentor": mentor, "a1": a1, "a2": a2}
    await cleanup([mentor, a1, a2], [])


async def _get(c: AsyncClient, H: dict) -> dict:
    g = await c.get(
        "/api/v1/frequencia", headers=H,
        params={"turma": TURMA, "data": DATA, "turno": "MANHA"},
    )
    assert g.status_code == 200, g.text
    return {row["aluno_nome"]: row for row in g.json()}


@pytest.mark.asyncio
async def test_lancar_atestado_idempotencia(ctx: dict) -> None:
    H = auth(ctx["mentor"])
    async with _client() as c:
        r = await c.post(
            "/api/v1/frequencia",
            headers=H,
            json={
                "turma": TURMA, "data": DATA, "turno": "MANHA",
                "lancamentos": [
                    {"aluno_id": str(ctx["a1"]), "status": "PRESENTE"},
                    {"aluno_id": str(ctx["a2"]), "status": "FALTA"},
                ],
            },
        )
        assert r.status_code == 200, r.text

        rows = await _get(c, H)
        assert rows["Aluno1"]["status"] == "PRESENTE"
        assert rows["Aluno2"]["status"] == "FALTA"
        freq_a1, freq_a2 = rows["Aluno1"]["freq_id"], rows["Aluno2"]["freq_id"]

        # Atestado em falta → Justificado
        at = await c.post(f"/api/v1/frequencia/{freq_a2}/atestado", headers=H, files=PDF)
        assert at.status_code == 200, at.text
        # Atestado em presente → 400
        bad = await c.post(f"/api/v1/frequencia/{freq_a1}/atestado", headers=H, files=PDF)
        assert bad.status_code == 400

        rows2 = await _get(c, H)
        assert rows2["Aluno2"]["status"] == "JUSTIFICADO"
        assert rows2["Aluno2"]["tem_atestado"] is True

        # Idempotência: relançar a2 como Falta não duplica e mantém Justificado (atestado prevalece)
        r2 = await c.post(
            "/api/v1/frequencia", headers=H,
            json={"turma": TURMA, "data": DATA, "turno": "MANHA",
                  "lancamentos": [{"aluno_id": str(ctx["a2"]), "status": "FALTA"}]},
        )
        assert r2.status_code == 200
        rows3 = await _get(c, H)
        assert rows3["Aluno2"]["freq_id"] == freq_a2  # mesmo registro
        assert rows3["Aluno2"]["status"] == "JUSTIFICADO"

        # Remover atestado → Falta
        rm = await c.delete(f"/api/v1/frequencia/{freq_a2}/atestado", headers=H)
        assert rm.status_code == 200
        rows4 = await _get(c, H)
        assert rows4["Aluno2"]["status"] == "FALTA"
        assert rows4["Aluno2"]["tem_atestado"] is False


@pytest.mark.asyncio
async def test_status_lancavel_invalido(ctx: dict) -> None:
    H = auth(ctx["mentor"])
    async with _client() as c:
        r = await c.post(
            "/api/v1/frequencia", headers=H,
            json={"turma": TURMA, "data": DATA, "turno": "MANHA",
                  "lancamentos": [{"aluno_id": str(ctx["a1"]), "status": "JUSTIFICADO"}]},
        )
        assert r.status_code == 400
