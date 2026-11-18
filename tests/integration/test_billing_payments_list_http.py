from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def make_client(role="ADMIN"):
    container = ApplicationContainer(database_path=":memory:")
    user = User(uuid4(), f"{role.lower()}@example.test", "hashed-password", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=TEST_TENANT_ID, role=role)
    student_id = uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) VALUES (?, ?, ?, ?, ?, 1)",
            (str(student_id), str(TEST_TENANT_ID), "Ada", "Lovelace", None),
        )
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=TEST_TENANT_ID,
    )
    client = TestClient(create_app(container))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, container, student_id


def test_list_payments_is_paginated_and_tenant_scoped():
    client, container, student_id = make_client()
    other_tenant = uuid4()
    other_student = uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) VALUES (?, ?, ?, ?, ?, 1)",
            (str(other_student), str(other_tenant), "Other", "Tenant", None),
        )

    charge = client.post(
        "/billing/charges",
        json={
            "student_id": str(student_id),
            "description": "Frais",
            "amount": "100.00",
            "currency": "USD",
        },
    ).json()
    client.post(
        "/billing/payments",
        json={
            "charge_id": charge["id"],
            "amount": "40.00",
            "currency": "USD",
            "idempotency_key": "pay-list-1",
        },
    )

    # Direct insert of foreign-tenant payment must stay invisible.
    with container._database.connect() as connection:
        connection.execute(
            """INSERT INTO billing_charges
            (id, tenant_id, student_id, description, amount, currency, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')""",
            (str(uuid4()), str(other_tenant), str(other_student), "Foreign", "10.00", "USD", None),
        )

    response = client.get("/billing/payments?limit=10&offset=0")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["limit"] == 10
    assert payload["offset"] == 0
    assert len(payload["items"]) == 1
    assert payload["items"][0]["student_id"] == str(student_id)


def test_list_payments_filters_by_student_and_status():
    client, _, student_id = make_client(role="ACCOUNTANT")
    charge = client.post(
        "/billing/charges",
        json={
            "student_id": str(student_id),
            "description": "Frais",
            "amount": "80.00",
            "currency": "CDF",
        },
    ).json()
    client.post(
        "/billing/payments",
        json={
            "charge_id": charge["id"],
            "amount": "20.00",
            "currency": "CDF",
            "idempotency_key": "pay-filter-1",
        },
    )

    filtered = client.get(
        f"/billing/payments?student_id={student_id}&status=CONFIRMED"
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    empty = client.get(f"/billing/payments?student_id={uuid4()}")
    assert empty.status_code == 404


def test_list_payments_rejects_unauthorized_role():
    client, _, _ = make_client(role="TEACHER")
    response = client.get("/billing/payments")
    assert response.status_code == 403


def test_list_arrears_detects_overdue_partial_payments():
    client, _, student_id = make_client(role="CASHIER")
    past = (date.today() - timedelta(days=5)).isoformat()
    charge = client.post(
        "/billing/charges",
        json={
            "student_id": str(student_id),
            "description": "Frais en retard",
            "amount": "100.00",
            "currency": "USD",
            "due_date": past,
        },
    ).json()
    client.post(
        "/billing/payments",
        json={
            "charge_id": charge["id"],
            "amount": "30.00",
            "currency": "USD",
            "idempotency_key": "arrears-1",
        },
    )

    response = client.get("/billing/arrears?overdue_only=true")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    item = payload["items"][0]
    assert item["amount_due"] == "100.00"
    assert item["amount_paid"] == "30.00"
    assert item["amount_remaining"] == "70.00"
    assert item["overdue"] is True


def test_direction_dashboard_uses_real_balances():
    client, _, student_id = make_client(role="DIRECTION")
    charge = client.post(
        "/billing/charges",
        json={
            "student_id": str(student_id),
            "description": "Scolarite",
            "amount": "200.00",
            "currency": "USD",
        },
    ).json()
    client.post(
        "/billing/payments",
        json={
            "charge_id": charge["id"],
            "amount": "50.00",
            "currency": "USD",
            "idempotency_key": "dash-1",
        },
    )

    response = client.get("/dashboard/direction")
    assert response.status_code == 200
    payload = response.json()
    assert payload["active_students"] == 1
    assert payload["expected_amounts"][0]["amount"] == "200.00"
    assert payload["paid_amounts"][0]["amount"] == "50.00"
    assert payload["remaining_amounts"][0]["amount"] == "150.00"
    assert payload["recovery_rates"][0]["rate_percent"] == "25.00"


def test_direction_dashboard_rejects_cashier():
    client, _, _ = make_client(role="CASHIER")
    response = client.get("/dashboard/direction")
    assert response.status_code == 403
