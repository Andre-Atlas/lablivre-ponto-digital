"""Integração US4: exportação do relatório semanal (CSV e Excel; aluno pendente marcado)."""

import csv
import io
from collections.abc import AsyncGenerator

import openpyxl
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
        tipo=TipoUsuario.STAFF, role=RoleAdmin.NONE, turma="Turma 1", nome="Mentor"
    )
    a1 = await seed_user(
        tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma 1", nome="Aluno Um"
    )
    a2 = await seed_user(
        tipo=TipoUsuario.ALUNO, role=RoleAdmin.NONE, turma="Turma 1", nome="Aluno Dois"
    )
    lo1 = await seed_lo(1, "LO 1")
    lo2 = await seed_lo(2, "LO 2")
    async with _client() as c:
        await c.post(
            "/api/v1/admin/avaliacoes",
            json={
                "user_id": str(a1),
                "semana": 3,
                "niveis": {str(lo1): 2, str(lo2): 4},
                "comentario": "ok",
            },
            headers=auth(mentor),
        )
    # a2 left pending
    yield {"mentor": mentor, "a1": a1, "a2": a2, "lo1": lo1, "lo2": lo2}
    await cleanup([mentor, a1, a2], [lo1, lo2])


@pytest.mark.asyncio
async def test_export_csv_and_excel(env: dict) -> None:
    async with _client() as c:
        csv_resp = await c.get(
            "/api/v1/admin/avaliacoes/export?turma=Turma%201&semana=3&format=csv",
            headers=auth(env["mentor"]),
        )
        xlsx_resp = await c.get(
            "/api/v1/admin/avaliacoes/export?turma=Turma%201&semana=3&format=excel",
            headers=auth(env["mentor"]),
        )
    assert csv_resp.status_code == 200 and xlsx_resp.status_code == 200

    rows = list(csv.reader(io.StringIO(csv_resp.text)))
    header = rows[0]
    assert "LO1" in header and "LO2" in header and "Status" in header
    by_name = {r[0]: r for r in rows[1:]}
    i_status = header.index("Status")
    i_lo1 = header.index("LO1")
    assert by_name["Aluno Um"][i_status] == "AVALIADO"
    assert by_name["Aluno Um"][i_lo1] == "2"
    assert by_name["Aluno Dois"][i_status] == "PENDENTE"
    assert by_name["Aluno Dois"][i_lo1] == ""  # pending → no level

    wb = openpyxl.load_workbook(io.BytesIO(xlsx_resp.content))
    ws = wb.active
    xheader = [c.value for c in next(ws.iter_rows())]
    assert "LO1" in xheader and "Status" in xheader
