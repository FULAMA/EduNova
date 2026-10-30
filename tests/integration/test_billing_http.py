from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from src.billing.application.service import BillingService, BillingSummary, Charge, Payment
from src.billing.domain.money import Currency, Money
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
    assert summary.json()["balances"] == [{
        "currency": "USD", "total_charged": "100.00",
        "total_paid": "40.00", "outstanding": "60.00",
    }]


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
    assert summary["balances"][0]["total_paid"] == "0.00"
    assert summary["balances"][0]["outstanding"] == "100.00"
    replacement = client.post("/billing/payments", json={
        "charge_id": charge["id"], "amount": "40.00", "currency": "USD", "idempotency_key": "replacement-1",
    })
    assert replacement.status_code == 200
    final_summary = client.get(f"/billing/students/{student_id}/summary").json()
    assert final_summary["balances"][0]["total_paid"] == "40.00"
    assert final_summary["balances"][0]["outstanding"] == "60.00"
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



def test_billing_summary_keeps_currencies_separate():
    client, student_id = make_client()
    usd = client.post("/billing/charges", json={
        "student_id": str(student_id), "description": "Scolarite",
        "amount": "100.00", "currency": "USD",
    }).json()
    cdf = client.post("/billing/charges", json={
        "student_id": str(student_id), "description": "Uniforme",
        "amount": "50000.00", "currency": "CDF",
    }).json()
    client.post("/billing/payments", json={
        "charge_id": usd["id"], "amount": "25.00", "currency": "USD", "idempotency_key": "usd-balance",
    })
    client.post("/billing/payments", json={
        "charge_id": cdf["id"], "amount": "10000.00", "currency": "CDF", "idempotency_key": "cdf-balance",
    })

    summary = client.get(f"/billing/students/{student_id}/summary").json()
    balances = {item["currency"]: item for item in summary["balances"]}
    assert balances["USD"]["outstanding"] == "75.00"
    assert balances["CDF"]["outstanding"] == "40000.00"
    assert balances["USD"]["total_paid"] == "25.00"
    assert balances["CDF"]["total_paid"] == "10000.00"


def test_billing_balance_excludes_payments_for_cancelled_charges():
    tenant_id = uuid4()
    student_id = uuid4()
    actor_id = uuid4()
    active_charge_id = uuid4()
    cancelled_charge_id = uuid4()
    active_charge = Charge(
        id=active_charge_id, tenant_id=tenant_id, student_id=student_id,
        description="Frais actifs", amount=Money(Decimal("100.00"), Currency.USD),
        due_date=None, status="OPEN",
    )
    cancelled_charge = Charge(
        id=cancelled_charge_id, tenant_id=tenant_id, student_id=student_id,
        description="Frais annules", amount=Money(Decimal("50.00"), Currency.USD),
        due_date=None, status="CANCELLED",
    )
    now = datetime.now()
    active_payment = Payment(
        id=uuid4(), tenant_id=tenant_id, charge_id=active_charge_id,
        student_id=student_id, amount=Money(Decimal("30.00"), Currency.USD),
        idempotency_key="active-payment", status="CONFIRMED",
        recorded_by=actor_id, recorded_at=now, receipt_number="R-ACTIVE",
    )
    cancelled_payment = Payment(
        id=uuid4(), tenant_id=tenant_id, charge_id=cancelled_charge_id,
        student_id=student_id, amount=Money(Decimal("20.00"), Currency.USD),
        idempotency_key="cancelled-payment", status="CONFIRMED",
        recorded_by=actor_id, recorded_at=now, receipt_number="R-CANCELLED",
    )

    balances = BillingService.calculate_balances(BillingSummary(
        charges=(active_charge, cancelled_charge),
        payments=(active_payment, cancelled_payment),
    ))

    assert len(balances) == 1
    assert balances[0].total_charged == Decimal("100.00")
    assert balances[0].total_paid == Decimal("30.00")
    assert balances[0].outstanding == Decimal("70.00")
