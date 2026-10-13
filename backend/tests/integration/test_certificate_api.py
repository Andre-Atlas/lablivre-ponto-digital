"""Testes de integração da API de atestados médicos (T013, T019, T026).

Usam o banco sqlite de testes (via async_session_maker) e o cliente ASGI.
Cada teste semeia seus próprios usuários com UUIDs únicos e limpa ao final.
"""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.adapters.auth.jwt_handler import create_access_token
from app.adapters.persistence.database import async_session_maker
from app.adapters.persistence.orm_models import CertificateDay as CertificateDayModel
from app.adapters.persistence.orm_models import Checkin as CheckinModel
from app.adapters.persistence.orm_models import Device as DeviceModel
from app.adapters.persistence.orm_models import MedicalCertificate as CertModel
from app.adapters.persistence.orm_models import User as UserModel
from app.domain.enums import RoleAdmin, StatusCheckin, TipoUsuario
from app.main import app

PDF = ("atestado.pdf", b"%PDF-1.4 conteudo de teste", "application/pdf")


def _auth(user_id: uuid.UUID) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user_id)})}"}


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


@pytest_asyncio.fixture
async def actors() -> AsyncGenerator[dict, None]:
    """Cria um admin e um aluno (Turma 1), devolve ids/token, e limpa ao final."""
    admin_id = uuid.uuid4()
    aluno_id = uuid.uuid4()
    device_id = uuid.uuid4()
    now = datetime.now(UTC)
    async with async_session_maker() as s:
        s.add(
            UserModel(
                id=admin_id,
                email=f"admin_{admin_id}@t.com",
                nome="Admin T",
                tipo=TipoUsuario.STAFF,
                role=RoleAdmin.ADMIN,
                turma_ou_equipe="Equipe",
                oauth_provider="google",
                oauth_sub=str(admin_id),
                ativo=True,
                admin_aprovado=True,
                criado_em=now,
                atualizado_em=now,
            )
        )
        s.add(
            UserModel(
                id=aluno_id,
                email=f"aluno_{aluno_id}@t.com",
                nome="Aluno T",
                tipo=TipoUsuario.ALUNO,
                role=RoleAdmin.NONE,
                turma_ou_equipe="Turma 1",
                oauth_provider="google",
                oauth_sub=str(aluno_id),
                ativo=True,
                admin_aprovado=True,
                criado_em=now,
                atualizado_em=now,
            )
        )
        s.add(
            DeviceModel(
                id=device_id,
                user_id=aluno_id,
                mac_address=f"AA:BB:{str(aluno_id)[:2]}:00:00:01",
                os_type="web",
                principal=True,
                registrado_em=now,
            )
        )
        await s.commit()

    yield {"admin_id": admin_id, "aluno_id": aluno_id, "device_id": device_id}

    async with async_session_maker() as s:
        for uid in (aluno_id, admin_id):
            certs = (
                await s.execute(CertModel.__table__.select().where(CertModel.user_id == uid))
            ).all()
            for c in certs:
                await s.execute(
                    CertificateDayModel.__table__.delete().where(
                        CertificateDayModel.certificate_id == c.id
                    )
                )
            await s.execute(CertModel.__table__.delete().where(CertModel.user_id == uid))
            await s.execute(CheckinModel.__table__.delete().where(CheckinModel.user_id == uid))
            await s.execute(DeviceModel.__table__.delete().where(DeviceModel.user_id == uid))
            await s.execute(UserModel.__table__.delete().where(UserModel.id == uid))
        await s.commit()


async def _seed_checkin(
    aluno_id: uuid.UUID, device_id: uuid.UUID, ref: str, status: StatusCheckin
) -> None:
    async with async_session_maker() as s:
        s.add(
            CheckinModel(
                id=uuid.uuid4(),
                user_id=aluno_id,
                device_id=device_id,
                hora_checkin=datetime.now(UTC),
                status=status,
                turno_referencia=ref,
                criado_em=datetime.now(UTC),
            )
        )
        await s.commit()


# ─────────────────────────── US1: record ───────────────────────────


@pytest.mark.asyncio
async def test_record_happy_path_links_all_absent_shifts(actors: dict) -> None:
    data = {
        "user_id": str(actors["aluno_id"]),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
        "observacao": "5 dias",
    }
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["admin_id"]),
        )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "ACTIVE"
    assert body["dias_justificados"] == 5
    refs = {d["turno_referencia"] for d in body["dias"]}
    assert "2026-10-05_MANHA" in refs and "2026-10-09_MANHA" in refs


@pytest.mark.asyncio
async def test_record_excludes_shift_with_present_checkin(actors: dict) -> None:
    await _seed_checkin(
        actors["aluno_id"], actors["device_id"], "2026-10-05_MANHA", StatusCheckin.PRESENTE
    )
    data = {
        "user_id": str(actors["aluno_id"]),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
    }
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["admin_id"]),
        )
    assert r.status_code == 201, r.text
    body = r.json()
    refs = {d["turno_referencia"] for d in body["dias"]}
    assert "2026-10-05_MANHA" not in refs
    assert body["dias_justificados"] == 4


@pytest.mark.asyncio
async def test_record_links_already_justificado_shift(actors: dict) -> None:
    await _seed_checkin(
        actors["aluno_id"], actors["device_id"], "2026-10-05_MANHA", StatusCheckin.JUSTIFICADO
    )
    data = {
        "user_id": str(actors["aluno_id"]),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
    }
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["admin_id"]),
        )
    assert r.status_code == 201, r.text
    refs = {d["turno_referencia"] for d in r.json()["dias"]}
    assert "2026-10-05_MANHA" in refs  # já justificado continua vinculado


@pytest.mark.asyncio
async def test_record_rejects_end_before_start(actors: dict) -> None:
    data = {
        "user_id": str(actors["aluno_id"]),
        "periodo_inicio": "2026-10-09",
        "periodo_fim": "2026-10-05",
    }
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["admin_id"]),
        )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_record_rejects_bad_content_type(actors: dict) -> None:
    data = {
        "user_id": str(actors["aluno_id"]),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
    }
    files = {"documento": ("nota.txt", b"texto", "text/plain")}
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados", data=data, files=files, headers=_auth(actors["admin_id"])
        )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_record_rejects_non_aluno(actors: dict) -> None:
    # admin é STAFF → não elegível como sujeito de atestado
    data = {
        "user_id": str(actors["admin_id"]),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
    }
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["admin_id"]),
        )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_record_rbac_non_admin_forbidden(actors: dict) -> None:
    data = {
        "user_id": str(actors["aluno_id"]),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
    }
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["aluno_id"]),
        )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_record_missing_token_unauthorized(actors: dict) -> None:
    data = {
        "user_id": str(actors["aluno_id"]),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
    }
    async with _client() as c:
        r = await c.post("/api/v1/admin/certificados", data=data, files={"documento": PDF})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_record_aluno_not_found(actors: dict) -> None:
    data = {
        "user_id": str(uuid.uuid4()),
        "periodo_inicio": "2026-10-05",
        "periodo_fim": "2026-10-09",
    }
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["admin_id"]),
        )
    assert r.status_code == 404


# ─────────────────────────── US2: read / list / document ───────────────────────────


async def _record(actors: dict, inicio: str = "2026-10-05", fim: str = "2026-10-09") -> str:
    data = {"user_id": str(actors["aluno_id"]), "periodo_inicio": inicio, "periodo_fim": fim}
    async with _client() as c:
        r = await c.post(
            "/api/v1/admin/certificados",
            data=data,
            files={"documento": PDF},
            headers=_auth(actors["admin_id"]),
        )
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest.mark.asyncio
async def test_get_and_list_and_document(actors: dict) -> None:
    cert_id = await _record(actors)
    async with _client() as c:
        detail = await c.get(
            f"/api/v1/admin/certificados/{cert_id}", headers=_auth(actors["admin_id"])
        )
        listing = await c.get(
            f"/api/v1/admin/certificados?user_id={actors['aluno_id']}",
            headers=_auth(actors["admin_id"]),
        )
        doc_admin = await c.get(
            f"/api/v1/admin/certificados/{cert_id}/documento", headers=_auth(actors["admin_id"])
        )
        doc_student = await c.get(
            f"/api/v1/admin/certificados/{cert_id}/documento", headers=_auth(actors["aluno_id"])
        )
        missing = await c.get(
            f"/api/v1/admin/certificados/{uuid.uuid4()}", headers=_auth(actors["admin_id"])
        )
    assert detail.status_code == 200 and len(detail.json()["dias"]) == 5
    assert listing.status_code == 200 and any(x["id"] == cert_id for x in listing.json())
    assert doc_admin.status_code == 200 and doc_admin.headers["content-type"].startswith(
        "application/pdf"
    )
    assert doc_student.status_code == 403
    assert missing.status_code == 404


# ─────────────────────────── US3: revoke ───────────────────────────


@pytest.mark.asyncio
async def test_revoke_reverts_and_conflicts(actors: dict) -> None:
    cert_id = await _record(actors)
    async with _client() as c:
        rev = await c.post(
            f"/api/v1/admin/certificados/{cert_id}/revogar",
            json={"motivo": "documento inválido"},
            headers=_auth(actors["admin_id"]),
        )
        again = await c.post(
            f"/api/v1/admin/certificados/{cert_id}/revogar", headers=_auth(actors["admin_id"])
        )
    assert rev.status_code == 200, rev.text
    body = rev.json()
    assert body["status"] == "REVOKED" and body["revogado_por"] is not None
    assert all(d["ativo"] is False for d in body["dias"])
    assert again.status_code == 409
