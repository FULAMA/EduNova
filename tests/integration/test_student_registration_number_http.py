"""
Tests d'intégration HTTP — Décision 45 (Option A : Matricule scolaire et déduplication).

Vérifie :
1. Création d'élève sans matricule (optionnel, UUID interne immuable)
2. Création d'élève avec matricule explicite
3. Rejet de collision sur matricule identique au sein du même tenant (409 Conflict)
4. Tolérance du même matricule entre deux tenants distincts (isolation multi-tenant)
5. Mise à jour du matricule d'un élève
6. Rejet de collision lors d'une mise à jour vers un matricule déjà pris (409 Conflict)
7. Liste et détail des élèves avec leur matricule
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def _make_client(role: str = "ADMIN", tenant_id=TEST_TENANT_ID):
    container = ApplicationContainer(database_path=":memory:")
    user = User(uuid4(), f"{role.lower()}-{uuid4().hex[:6]}@edunova.test", "hashed-pass", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=tenant_id, role=role)

    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=tenant_id,
    )
    client = TestClient(create_app(container))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, container


def test_create_student_without_registration_number():
    client, _ = _make_client(role="ADMIN")

    resp = client.post(
        "/students",
        json={
            "first_name": "Jean",
            "last_name": "Mukendi",
            "email": "jean.mukendi@test.cd",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["first_name"] == "Jean"
    assert data["last_name"] == "Mukendi"
    assert data["registration_number"] is None
    assert "id" in data


def test_create_student_with_registration_number():
    client, _ = _make_client(role="ADMIN")

    resp = client.post(
        "/students",
        json={
            "first_name": "Marie",
            "last_name": "Kabasele",
            "registration_number": "MAT-2026-0042",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["first_name"] == "Marie"
    assert data["registration_number"] == "MAT-2026-0042"


def test_create_student_rejects_duplicate_registration_number_in_same_tenant():
    client, _ = _make_client(role="ADMIN")

    client.post(
        "/students",
        json={"first_name": "Eleve", "last_name": "Un", "registration_number": "MAT-UNIQUE-01"},
    )

    # Tentative d'un second élève avec le même matricule
    resp = client.post(
        "/students",
        json={"first_name": "Eleve", "last_name": "Deux", "registration_number": "MAT-UNIQUE-01"},
    )
    assert resp.status_code == 409
    assert "matricule scolaire est deja attribue" in resp.json()["detail"]


def test_same_registration_number_allowed_in_different_tenants():
    client_a, container = _make_client(role="ADMIN", tenant_id=TEST_TENANT_ID)

    resp_a = client_a.post(
        "/students",
        json={"first_name": "Eleve", "last_name": "TenantA", "registration_number": "MAT-COMMUN-99"},
    )
    assert resp_a.status_code == 201

    # Création sur tenant B
    other_tenant = uuid4()
    user_b = User(uuid4(), f"admin-{uuid4().hex[:6]}@other.test", "pwd", "ADMIN")
    container._user_repository().save(user_b)
    seed_membership(container, user_b.id, tenant_id=other_tenant, role="ADMIN")
    token_b = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user_b.id, role="ADMIN", tenant_id=other_tenant,
    )
    client_b = TestClient(create_app(container))
    client_b.headers.update({"Authorization": f"Bearer {token_b}"})

    resp_b = client_b.post(
        "/students",
        json={"first_name": "Eleve", "last_name": "TenantB", "registration_number": "MAT-COMMUN-99"},
    )
    assert resp_b.status_code == 201
    assert resp_b.json()["registration_number"] == "MAT-COMMUN-99"


def test_update_student_registration_number():
    client, _ = _make_client(role="ADMIN")

    created = client.post(
        "/students",
        json={"first_name": "David", "last_name": "Ilunga"},
    ).json()
    student_id = created["id"]
    assert created["registration_number"] is None

    # Attribution d'un matricule lors de la mise à jour
    updated = client.put(
        f"/students/{student_id}",
        json={
            "first_name": "David",
            "last_name": "Ilunga",
            "registration_number": "MAT-2026-0099",
            "active": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["registration_number"] == "MAT-2026-0099"

    # Vérification par GET
    detail = client.get(f"/students/{student_id}").json()
    assert detail["registration_number"] == "MAT-2026-0099"


def test_update_student_rejects_duplicate_registration_number():
    client, _ = _make_client(role="ADMIN")

    client.post(
        "/students",
        json={"first_name": "Eleve", "last_name": "A", "registration_number": "MAT-PRISE"},
    )
    student_b = client.post(
        "/students",
        json={"first_name": "Eleve", "last_name": "B"},
    ).json()

    # Tentative d'attribuer MAT-PRISE à l'élève B
    conflict = client.put(
        f"/students/{student_b['id']}",
        json={
            "first_name": "Eleve",
            "last_name": "B",
            "registration_number": "MAT-PRISE",
            "active": True,
        },
    )
    assert conflict.status_code == 409
    assert "matricule scolaire est deja attribue" in conflict.json()["detail"]
