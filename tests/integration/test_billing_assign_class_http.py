from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def setup_class_billing_environment(role: str = "ADMIN", tenant_id=TEST_TENANT_ID):
    container = ApplicationContainer(database_path=":memory:")
    user = User(uuid4(), f"admin-{uuid4().hex[:6]}@example.test", "hashed-pass", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=tenant_id, role=role)

    # Seed academic year, period, class, and 3 students
    year_id = uuid4()
    period_id = uuid4()
    class_id = uuid4()
    student_ids = [uuid4(), uuid4(), uuid4()]

    with container._database.connect() as conn:
        # Academic year
        conn.execute(
            """INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status)
               VALUES (?, ?, '2026-2027', '2026-09-01', '2027-06-30', 'ACTIVE')""",
            (str(year_id), str(tenant_id)),
        )
        # Academic period
        conn.execute(
            """INSERT INTO academic_periods (id, tenant_id, academic_year_id, name, start_date, end_date)
               VALUES (?, ?, ?, 'Trimestre 1', '2026-09-01', '2026-12-15')""",
            (str(period_id), str(tenant_id), str(year_id)),
        )
        # Class
        conn.execute(
            """INSERT INTO academic_classes (id, tenant_id, name)
               VALUES (?, ?, '6e Primaire A')""",
            (str(class_id), str(tenant_id)),
        )
        # 3 Students & assignments
        for i, s_id in enumerate(student_ids):
            conn.execute(
                """INSERT INTO students (id, tenant_id, first_name, last_name, active)
                   VALUES (?, ?, ?, ?, 1)""",
                (str(s_id), str(tenant_id), f"Student{i}", "Test"),
            )
            conn.execute(
                """INSERT INTO student_assignments (id, tenant_id, student_id, academic_class_id, academic_year_id, status, created_by, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, '2026-09-01T08:00:00Z', '2026-09-01T08:00:00Z')""",
                (str(uuid4()), str(tenant_id), str(s_id), str(class_id), str(year_id), str(user.id)),
            )

    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=tenant_id,
    )
    client = TestClient(create_app(container))
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client, container, year_id, period_id, class_id, student_ids


def test_assign_fee_type_to_class_nominal():
    client, _, _, period_id, class_id, student_ids = setup_class_billing_environment(role="ADMIN")

    # 1. Create fee type
    fee = client.post("/billing/fee-types", json={
        "name": "Minerval T1",
        "category": "TUITION",
        "amount": "150.00",
        "currency": "USD",
        "academic_period_id": str(period_id),
        "applicability": "CLASS",
        "target_class_id": str(class_id),
    }).json()

    # 2. Publish fee type
    client.post(f"/billing/fee-types/{fee['id']}/publish")

    # 3. Assign to class
    res = client.post(
        f"/billing/fee-types/{fee['id']}/assign-class",
        json={
            "class_id": str(class_id),
            "academic_period_id": str(period_id),
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["total_eligible_students"] == 3
    assert data["assigned_count"] == 3
    assert data["already_assigned_count"] == 0
    assert len(data["assignments"]) == 3

    # 4. Check each student's billing summary
    for s_id in student_ids:
        summary = client.get(f"/billing/students/{s_id}/summary").json()
        assert len(summary["charges"]) == 1
        assert summary["charges"][0]["amount"] == "150.00"
        assert summary["charges"][0]["currency"] == "USD"
        assert summary["charges"][0]["description"] == "Minerval T1"


def test_assign_fee_type_to_class_is_idempotent():
    client, _, _, period_id, class_id, student_ids = setup_class_billing_environment(role="DIRECTION")

    fee = client.post("/billing/fee-types", json={
        "name": "Frais Informatique",
        "category": "LAB",
        "amount": "25.00",
        "currency": "USD",
        "academic_period_id": str(period_id),
        "applicability": "CLASS",
        "target_class_id": str(class_id),
    }).json()
    client.post(f"/billing/fee-types/{fee['id']}/publish")

    # First call
    first = client.post(
        f"/billing/fee-types/{fee['id']}/assign-class",
        json={"class_id": str(class_id), "academic_period_id": str(period_id)},
    )
    assert first.status_code == 201
    assert first.json()["assigned_count"] == 3

    # Second call (idempotency check)
    second = client.post(
        f"/billing/fee-types/{fee['id']}/assign-class",
        json={"class_id": str(class_id), "academic_period_id": str(period_id)},
    )
    assert second.status_code == 201
    data = second.json()
    assert data["total_eligible_students"] == 3
    assert data["assigned_count"] == 0
    assert data["already_assigned_count"] == 3

    # Check charges did not duplicate
    for s_id in student_ids:
        summary = client.get(f"/billing/students/{s_id}/summary").json()
        assert len(summary["charges"]) == 1


def test_assign_fee_type_to_class_draft_rejected():
    client, _, _, period_id, class_id, _ = setup_class_billing_environment(role="DIRECTION")

    fee = client.post("/billing/fee-types", json={
        "name": "Frais Brouillon",
        "category": "TUITION",
        "amount": "50.00",
        "currency": "USD",
        "academic_period_id": str(period_id),
        "applicability": "CLASS",
        "target_class_id": str(class_id),
    }).json()
    # DO NOT PUBLISH

    res = client.post(
        f"/billing/fee-types/{fee['id']}/assign-class",
        json={"class_id": str(class_id), "academic_period_id": str(period_id)},
    )
    assert res.status_code == 409
    assert "publie" in res.json()["detail"]


def test_assign_fee_type_to_class_target_class_mismatch():
    client, container, _, period_id, class_id, _ = setup_class_billing_environment(role="ADMIN")

    # Create second class
    other_class_id = uuid4()
    with container._database.connect() as conn:
        conn.execute(
            "INSERT INTO academic_classes (id, tenant_id, name) VALUES (?, ?, '6e Primaire B')",
            (str(other_class_id), str(TEST_TENANT_ID)),
        )

    fee = client.post("/billing/fee-types", json={
        "name": "Frais Dédié Classe A",
        "category": "TUITION",
        "amount": "60.00",
        "currency": "USD",
        "academic_period_id": str(period_id),
        "applicability": "CLASS",
        "target_class_id": str(class_id),
    }).json()
    client.post(f"/billing/fee-types/{fee['id']}/publish")

    # Try assigning to other_class_id
    res = client.post(
        f"/billing/fee-types/{fee['id']}/assign-class",
        json={"class_id": str(other_class_id), "academic_period_id": str(period_id)},
    )
    assert res.status_code == 409
    assert "cible" in res.json()["detail"]


def test_assign_fee_type_to_class_cashier_forbidden():
    client, _, _, period_id, class_id, _ = setup_class_billing_environment(role="CASHIER")

    res = client.post(
        f"/billing/fee-types/{uuid4()}/assign-class",
        json={"class_id": str(class_id), "academic_period_id": str(period_id)},
    )
    assert res.status_code == 403


def test_assign_fee_type_to_class_cross_tenant_isolation():
    client_a, _, _, period_a, class_a, _ = setup_class_billing_environment(tenant_id=TEST_TENANT_ID)

    # Setup tenant B
    other_tenant = uuid4()
    client_b, _, _, period_b, class_b, _ = setup_class_billing_environment(tenant_id=other_tenant)

    # Create and publish fee in tenant A
    fee_a = client_a.post("/billing/fee-types", json={
        "name": "Frais Tenant A",
        "category": "TUITION",
        "amount": "100.00",
        "currency": "USD",
        "academic_period_id": str(period_a),
        "applicability": "CLASS",
        "target_class_id": str(class_a),
    }).json()
    client_a.post(f"/billing/fee-types/{fee_a['id']}/publish")

    # Tenant B tries to assign Tenant A's fee type -> 404
    res = client_b.post(
        f"/billing/fee-types/{fee_a['id']}/assign-class",
        json={"class_id": str(class_b), "academic_period_id": str(period_b)},
    )
    assert res.status_code == 404
