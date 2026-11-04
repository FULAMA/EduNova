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
    user = User(uuid4(), "billing-admin@example.test", "hashed-password", role)
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
    return client, student_id


def test_billing_payment_is_idempotent_and_summary_is_tenant_scoped():
    client, student_id = make_client()
    charge = client.post("/billing/charges", json={
        "student_id": str(student_id), "description": "Frais scolaires",
        "amount": "100.00", "currency": "USD",
    })
    assert charge.status_code == 201

    payload = {"charge_id": charge.json()["id"], "amount": "40.00", "currency": "USD", "idempotency_key": "pay-1"}
    first = client.post("/billing/payments", json=payload)
    retry = client.post("/billing/payments", json=payload)
    assert first.status_code == 200
    assert retry.status_code == 200
    assert first.json()["id"] == retry.json()["id"]
    assert first.json()["receipt_number"] == retry.json()["receipt_number"]

    summary = client.get(f"/billing/students/{student_id}/summary")
    assert summary.status_code == 200
    assert len(summary.json()["charges"]) == 1
    assert len(summary.json()["payments"]) == 1
    assert summary.json()["balances"] == [{"charge_id": charge.json()["id"], "total_paid": "40.00", "remaining": "60.00"}]


def test_billing_correction_preserves_payment_and_marks_receipt_reversed():
    client, student_id = make_client(role="ACCOUNTANT")
    charge = client.post("/billing/charges", json={
        "student_id": str(student_id), "description": "Frais", "amount": "100.00", "currency": "USD",
    }).json()
    payment = client.post("/billing/payments", json={
        "charge_id": charge["id"], "amount": "40.00", "currency": "USD", "idempotency_key": "correction-1",
    }).json()
    corrected = client.post(f"/billing/payments/{payment['id']}/correction", json={"reason": "Erreur de saisie"})
    assert corrected.status_code == 200
    again = client.post(f"/billing/payments/{payment['id']}/correction", json={"reason": "Deuxieme tentative"})
    assert again.status_code == 409
    summary = client.get(f"/billing/students/{student_id}/summary").json()
    assert summary["payments"][0]["id"] == payment["id"]
    assert summary["payments"][0]["receipt_status"] == "REVERSED"
    assert summary["balances"] == [{"charge_id": charge["id"], "total_paid": "0.00", "remaining": "100.00"}]
    replacement = client.post("/billing/payments", json={
        "charge_id": charge["id"], "amount": "40.00", "currency": "USD", "idempotency_key": "replacement-1",
    })
    assert replacement.status_code == 200
    pdf = client.get(f"/billing/receipts/{payment['receipt_number']}/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content.startswith(b"%PDF-1.4")


def test_billing_rejects_unauthorized_role():
    client, student_id = make_client(role="TEACHER")
    response = client.get(f"/billing/students/{student_id}/summary")
    assert response.status_code == 403


def test_fee_catalogue_is_draft_then_publish_and_archive():
    client, _ = make_client(role="DIRECTION")
    created = client.post("/billing/fee-types", json={
        "name": "Inscription", "description": "Frais annuels", "category": "INSCRIPTION",
        "amount": "250.00", "currency": "USD", "applicability": "ESTABLISHMENT",
    })
    assert created.status_code == 201
    fee_type = created.json()
    assert fee_type["status"] == "DRAFT"
    published = client.post(f"/billing/fee-types/{fee_type['id']}/publish")
    assert published.status_code == 200
    assert published.json()["status"] == "PUBLISHED"
    archived = client.post(f"/billing/fee-types/{fee_type['id']}/archive")
    assert archived.status_code == 200
    assert archived.json()["status"] == "ARCHIVED"


def test_cashier_can_read_but_not_change_fee_catalogue():
    client, _ = make_client(role="CASHIER")
    assert client.get("/billing/fee-types").status_code == 200
    assert client.post("/billing/fee-types", json={
        "name": "Examen", "category": "EXAM", "amount": "10.00", "currency": "CDF",
    }).status_code == 403


def test_published_fee_assignment_uses_catalogue_amount_and_is_idempotent():
    client, student_id = make_client(role="DIRECTION")
    fee = client.post("/billing/fee-types", json={
        "name": "Travaux", "category": "ACTIVITY", "amount": "75.00", "currency": "CDF",
    }).json()
    client.post(f"/billing/fee-types/{fee['id']}/publish")
    first = client.post(f"/billing/fee-types/{fee['id']}/assign", json={"student_id": str(student_id)})
    retry = client.post(f"/billing/fee-types/{fee['id']}/assign", json={"student_id": str(student_id)})
    assert first.status_code == 201
    assert retry.status_code == 201
    assert first.json()["id"] == retry.json()["id"]
    assert first.json()["amount"] == "75.00"
    summary = client.get(f"/billing/students/{student_id}/summary").json()
    assert len(summary["charges"]) == 1
    assert summary["charges"][0]["currency"] == "CDF"


def test_draft_fee_cannot_be_assigned_and_client_cannot_override_amount():
    client, student_id = make_client(role="DIRECTION")
    fee = client.post("/billing/fee-types", json={
        "name": "Examen", "category": "EXAM", "amount": "10.00", "currency": "USD",
    }).json()
    response = client.post(f"/billing/fee-types/{fee['id']}/assign", json={
        "student_id": str(student_id), "amount": "1.00", "currency": "CDF",
    })
    assert response.status_code == 409


def test_billing_rejects_invalid_amount_and_currency_mismatch():
    client, student_id = make_client()
    charge = client.post("/billing/charges", json={
        "student_id": str(student_id), "description": "Contribution",
        "amount": "100.00", "currency": "CDF",
    }).json()

    assert client.post("/billing/payments", json={
        "charge_id": charge["id"], "amount": "1.00", "currency": "USD", "idempotency_key": "wrong-currency",
    }).status_code == 409
    assert client.post("/billing/payments", json={
        "charge_id": charge["id"], "amount": "0", "currency": "CDF", "idempotency_key": "zero",
    }).status_code == 422



def test_decimal_payment_parts_exactly_cover_charge():
    client, student_id = make_client()
    charge = client.post("/billing/charges", json={
        "student_id": str(student_id), "description": "Frais fractionnes",
        "amount": "0.30", "currency": "USD",
    })
    assert charge.status_code == 201
    charge_id = charge.json()["id"]

    first = client.post("/billing/payments", json={
        "charge_id": charge_id, "amount": "0.10", "currency": "USD",
        "idempotency_key": "decimal-part-1",
    })
    second = client.post("/billing/payments", json={
        "charge_id": charge_id, "amount": "0.20", "currency": "USD",
        "idempotency_key": "decimal-part-2",
    })

    assert first.status_code == 200
    assert second.status_code == 200
    summary = client.get(f"/billing/students/{student_id}/summary").json()
    assert summary["balances"] == [{"charge_id": charge_id, "total_paid": "0.30", "remaining": "0.00"}]



def test_billing_data_is_isolated_between_two_tenants():
    """A tenant cannot read or mutate another tenant's billing records."""
    from uuid import uuid4

    from tests.support.tenant import seed_membership

    container = ApplicationContainer(database_path=":memory:")
    tenant_a = uuid4()
    tenant_b = uuid4()

    def tenant_client(tenant_id, email):
        user = User(uuid4(), email, "hashed-password", "ADMIN")
        container._user_repository().save(user)
        seed_membership(container, user.id, tenant_id=tenant_id, role="ADMIN")
        token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
            user_id=user.id, role="ADMIN", tenant_id=tenant_id,
        )
        client = TestClient(create_app(container))
        client.headers.update({"Authorization": f"Bearer {token}"})
        return client

    client_a = tenant_client(tenant_a, "tenant-a@example.test")
    client_b = tenant_client(tenant_b, "tenant-b@example.test")

    def insert_student(tenant_id, first_name):
        student_id = uuid4()
        with container._database.connect() as connection:
            connection.execute(
                "INSERT INTO students (id, tenant_id, first_name, last_name, email, active) "
                "VALUES (?, ?, ?, ?, ?, 1)",
                (str(student_id), str(tenant_id), first_name, "Student", None),
            )
        return student_id

    student_a = insert_student(tenant_a, "TenantA")
    student_b = insert_student(tenant_b, "TenantB")

    charge_a_response = client_a.post("/billing/charges", json={
        "student_id": str(student_a), "description": "Tenant A charge",
        "amount": "100.00", "currency": "USD",
    })
    charge_b_response = client_b.post("/billing/charges", json={
        "student_id": str(student_b), "description": "Tenant B charge",
        "amount": "200.00", "currency": "USD",
    })
    assert charge_a_response.status_code == 201
    assert charge_b_response.status_code == 201
    charge_a = charge_a_response.json()
    charge_b = charge_b_response.json()

    payment_a_response = client_a.post("/billing/payments", json={
        "charge_id": charge_a["id"], "amount": "25.00", "currency": "USD",
        "idempotency_key": "tenant-a-payment",
    })
    assert payment_a_response.status_code == 200
    payment_a = payment_a_response.json()

    # A tenant cannot see the other tenant's student summary or receipt.
    assert client_b.get(f"/billing/students/{student_a}/summary").status_code == 404
    assert client_b.get(
        f"/billing/receipts/{payment_a['receipt_number']}/pdf"
    ).status_code == 404

    # A tenant cannot post a payment against another tenant's charge.
    cross_tenant_payment = client_b.post("/billing/payments", json={
        "charge_id": charge_a["id"], "amount": "10.00", "currency": "USD",
        "idempotency_key": "cross-tenant-payment",
    })
    assert cross_tenant_payment.status_code == 404

    # A tenant cannot reverse another tenant's payment.
    cross_tenant_correction = client_b.post(
        f"/billing/payments/{payment_a['id']}/correction",
        json={"reason": "Cross-tenant attempt"},
    )
    assert cross_tenant_correction.status_code == 404

    # Both tenants retain only their own billing data after rejected attempts.
    summary_a = client_a.get(f"/billing/students/{student_a}/summary")
    summary_b = client_b.get(f"/billing/students/{student_b}/summary")
    assert summary_a.status_code == summary_b.status_code == 200
    assert [item["id"] for item in summary_a.json()["charges"]] == [charge_a["id"]]
    assert [item["id"] for item in summary_a.json()["payments"]] == [payment_a["id"]]
    assert [item["id"] for item in summary_b.json()["charges"]] == [charge_b["id"]]
    assert summary_b.json()["payments"] == []
