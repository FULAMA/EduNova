"""
Tests d'intégration HTTP — Suivi des rappels et relances d'impayés (Décision 22).

Vérifie :
1. Enregistrement nominal d'une relance (SMS, EMAIL, PHONE, etc.).
2. Récupération de l'historique des relances pour une charge.
3. Multiples relances consécutives avec traçabilité chronologique.
4. Rejet d'un canal de relance non autorisé (400).
5. Rejet si la créance est déjà soldée / aucun arriéré (400).
6. Isolation multi-tenant stricte (404 si autre tenant).
7. Contrôle des rôles financiers (ADMIN, DIRECTION, ACCOUNTANT, CASHIER autorisés, STUDENT rejeté 403).
"""

from datetime import date, timedelta
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
    user = User(uuid4(), f"{role.lower()}-{uuid4()}@edunova.test", "hashed-pwd", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=tenant_id, role=role)
    student_id = uuid4()
    with container._database.connect() as conn:
        conn.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) "
            "VALUES (?, ?, ?, ?, ?, 1)",
            (str(student_id), str(tenant_id), "Test", "Student", None),
        )
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=tenant_id,
    )
    client = TestClient(create_app(container))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, container, student_id


def _create_charge(client, student_id, amount="150.00", currency="USD", due_date=None):
    body = {
        "student_id": str(student_id),
        "description": "Minerval T1",
        "amount": amount,
        "currency": currency,
    }
    if due_date is not None:
        body["due_date"] = due_date
    r = client.post("/billing/charges", json=body)
    assert r.status_code == 201, f"Charge creation failed: {r.text}"
    return r.json()


def test_record_arrear_reminder_nominal():
    client, _, student_id = _make_client(role="ADMIN")
    past_due = (date.today() - timedelta(days=5)).isoformat()
    charge = _create_charge(client, student_id, amount="200.00", due_date=past_due)
    charge_id = charge["id"]

    # Création d'une relance par SMS
    resp = client.post(
        f"/billing/arrears/{charge_id}/reminders",
        json={
            "channel": "SMS",
            "recipient": "+243812345678",
            "notes": "Premier rappel envoye au pere de l eleve.",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["charge_id"] == charge_id
    assert data["student_id"] == str(student_id)
    assert data["channel"] == "SMS"
    assert data["recipient"] == "+243812345678"
    assert data["notes"] == "Premier rappel envoye au pere de l eleve."
    assert "sent_at" in data
    assert "sent_by" in data


def test_list_arrear_reminders_history():
    client, _, student_id = _make_client(role="DIRECTION")
    charge = _create_charge(client, student_id, amount="100.00")
    charge_id = charge["id"]

    # Envoyer 2 rappels consécutifs
    client.post(
        f"/billing/arrears/{charge_id}/reminders",
        json={"channel": "SMS", "recipient": "+243810000001", "notes": "Rappel 1"},
    )
    client.post(
        f"/billing/arrears/{charge_id}/reminders",
        json={"channel": "EMAIL", "recipient": "parent@edunova.cd", "notes": "Rappel 2"},
    )

    # Récupérer l'historique
    resp = client.get(f"/billing/arrears/{charge_id}/reminders")
    assert resp.status_code == 200, resp.text
    reminders = resp.json()
    assert len(reminders) == 2
    # Ordre antichronologique
    assert reminders[0]["channel"] == "EMAIL"
    assert reminders[0]["notes"] == "Rappel 2"
    assert reminders[1]["channel"] == "SMS"
    assert reminders[1]["notes"] == "Rappel 1"


def test_record_arrear_reminder_rejects_invalid_channel():
    client, _, student_id = _make_client(role="ACCOUNTANT")
    charge = _create_charge(client, student_id, amount="100.00")
    charge_id = charge["id"]

    resp = client.post(
        f"/billing/arrears/{charge_id}/reminders",
        json={"channel": "WHATSAPP_UNSUPPORTED", "recipient": "user@test.cd"},
    )
    assert resp.status_code == 400
    assert "Canal de relance invalide" in resp.json()["detail"]


def test_record_arrear_reminder_rejects_fully_paid_charge():
    client, _, student_id = _make_client(role="CASHIER")
    charge = _create_charge(client, student_id, amount="100.00", currency="USD")
    charge_id = charge["id"]

    # Payer la charge intégralement
    pay_resp = client.post(
        "/billing/payments",
        json={
            "charge_id": charge_id,
            "amount": "100.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert pay_resp.status_code in (200, 201)

    # Tenter de relancer une charge déjà soldée
    resp = client.post(
        f"/billing/arrears/{charge_id}/reminders",
        json={"channel": "PHONE", "recipient": "+243812345678", "notes": "Rappel indu"},
    )
    assert resp.status_code == 400
    assert "aucun arriere impaye" in resp.json()["detail"]


def test_arrear_reminders_cross_tenant_isolation():
    client_a, container, student_a = _make_client(role="ADMIN", tenant_id=TEST_TENANT_ID)
    charge_a = _create_charge(client_a, student_a, amount="100.00")
    charge_id = charge_a["id"]

    # Créer un utilisateur et client sur un autre tenant
    other_tenant = uuid4()
    user_b = User(uuid4(), f"admin-{uuid4()}@other.test", "pwd", "ADMIN")
    container._user_repository().save(user_b)
    seed_membership(container, user_b.id, tenant_id=other_tenant, role="ADMIN")
    token_b = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user_b.id, role="ADMIN", tenant_id=other_tenant,
    )
    client_b = TestClient(create_app(container))
    client_b.headers.update({"Authorization": f"Bearer {token_b}"})

    # Le client B tente de relancer la charge de A -> 404
    resp = client_b.post(
        f"/billing/arrears/{charge_id}/reminders",
        json={"channel": "EMAIL", "recipient": "test@other.cd"},
    )
    assert resp.status_code == 404

    # Le client B tente de lire les relances de A -> 404
    resp_get = client_b.get(f"/billing/arrears/{charge_id}/reminders")
    assert resp_get.status_code == 404


def test_arrear_reminders_role_rbac_forbidden():
    client, _, student_id = _make_client(role="STUDENT")
    charge_id = uuid4()

    # Rôle non financier interdit
    resp = client.post(
        f"/billing/arrears/{charge_id}/reminders",
        json={"channel": "EMAIL", "recipient": "test@other.cd"},
    )
    assert resp.status_code == 403

    resp_get = client.get(f"/billing/arrears/{charge_id}/reminders")
    assert resp_get.status_code == 403
