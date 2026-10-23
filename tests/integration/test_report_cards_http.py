from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus, StudentAcademicRecord
from src.identity.domain.entities.user import User
from src.infrastructure.repositories.sqlite_deliberation_repository import SQLiteDeliberationRepository
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def authenticated_client(container, user, tenant_id=TEST_TENANT_ID):
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=user.role, tenant_id=tenant_id,
    )
    client = TestClient(create_app(container))
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def test_report_card_is_published_only_after_validated_deliberation_and_is_student_scoped():
    container = ApplicationContainer(database_path=":memory:")
    admin = User(uuid4(), "admin-report-card@example.test", "hash", "ADMIN")
    student_user = User(uuid4(), "student-report-card@example.test", "hash", "STUDENT")
    container._user_repository().save(admin)
    container._user_repository().save(student_user)
    seed_membership(container, admin.id, role="ADMIN")
    seed_membership(container, student_user.id, role="STUDENT")
    admin_client = authenticated_client(container, admin)
    student_client = authenticated_client(container, student_user)

    student_id, period_id, deliberation_id = uuid4(), uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(TEST_TENANT_ID), "Eleve", "Bulletin", None, None, 1),
        )
    container._academic_period_repository().save(AcademicPeriod(
        period_id, TEST_TENANT_ID, "Trimestre 1", date(2026, 9, 1), date(2026, 12, 20),
    ))
    container._student_academic_record_repository().save(StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID, student_id=student_id, academic_period_id=period_id,
        subject_results=(), general_average=14, failed_subjects=0,
        credits_obtained=20, total_credits=30, status=AcademicRecordStatus.VALIDATED,
    ))
    deliberation = SQLiteDeliberationRepository(container._database).save(Deliberation(
        student_id=student_id, average=14, failed_subjects=0,
        decision=DeliberationDecision.ADMITTED, tenant_id=TEST_TENANT_ID,
        academic_period_id=period_id, record_version=1, id=deliberation_id,
        status="VALIDATED", version=2, created_by=admin.id,
        created_at=datetime.now(timezone.utc), validated_by=admin.id,
        validated_at=datetime.now(timezone.utc),
    ))
    assert admin_client.post("/student-links", json={
        "user_id": str(student_user.id), "student_id": str(student_id),
    }).status_code == 201

    prepared = admin_client.post(
        f"/report-cards/{student_id}/{period_id}/prepare",
        json={"deliberation_id": str(deliberation.id)},
    )
    assert prepared.status_code == 201
    report_card_id = prepared.json()["id"]
    assert prepared.json()["status"] == "DRAFT"
    assert student_client.get("/report-cards").json() == []

    published = admin_client.post(f"/report-cards/{report_card_id}/publish")
    assert published.status_code == 200
    assert published.json()["status"] == "ISSUED"
    cards = student_client.get("/report-cards")
    assert cards.status_code == 200
    assert cards.json()[0]["id"] == report_card_id
    assert cards.json()[0]["snapshot"]["record_version"] == 1
    assert student_client.get(f"/report-cards/{report_card_id}").status_code == 200
    pdf = student_client.get(f"/report-cards/{report_card_id}/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")
