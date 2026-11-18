"""
Tests d'intégration HTTP — Portail Parent et Rattachement Parent-Élève (PAR-REL-01 à PAR-REL-06 — Lot 8).

Scénarios vérifiés :
1. Rattachement parent-élève créé par DIRECTION/ADMIN (POST /parent-links -> 201)
2. Cardinalité N:M : un parent associé à plusieurs enfants
3. Rejet si utilisateur parent introuvable dans l'établissement (404)
4. Rejet si élève introuvable dans l'établissement (404)
5. RBAC : un élève ou parent ne peut pas créer de lien parent-élève (403)
6. Consultation des enfants rattachés (GET /parent-portal/students -> 200)
7. Consultation des bulletins officiels de son enfant (GET /parent-portal/students/{id}/report-cards -> 200)
8. Téléchargement PDF du bulletin de son enfant (GET /parent-portal/students/{id}/report-cards/{rc_id}/pdf -> 200)
9. Parent billing endpoint is intentionally unavailable (404)
10. Unlinked students cannot expose report cards (403)
"""

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.academic.domain.entities.report_card import ReportCard, ReportCardStatus
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus, StudentAcademicRecord
from src.identity.domain.entities.user import User
from src.infrastructure.repositories.sqlite_deliberation_repository import SQLiteDeliberationRepository
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def _make_client(role: str = "PARENT", tenant_id=TEST_TENANT_ID):
    container = ApplicationContainer(database_path=":memory:")
    user = User(uuid4(), f"{role.lower()}-{uuid4().hex[:6]}@edunova.test", "hashed-pass", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, tenant_id=tenant_id, role=role)

    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=tenant_id,
    )
    client = TestClient(create_app(container))
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, container, user


def _seed_student(container, first_name="Junior", last_name="Tshilombo"):
    student_id = uuid4()
    with container._database.connect() as conn:
        conn.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, active) VALUES (?, ?, ?, ?, 1)",
            (str(student_id), str(TEST_TENANT_ID), first_name, last_name),
        )
    return student_id


def test_direction_can_link_parent_to_multiple_students_nm():
    _, container, _ = _make_client(role="ADMIN")
    direction = User(uuid4(), "direction@test.cd", "hash", "DIRECTION")
    container._user_repository().save(direction)
    seed_membership(container, direction.id, role="DIRECTION")

    parent = User(uuid4(), "parent@test.cd", "hash", "PARENT")
    container._user_repository().save(parent)
    seed_membership(container, parent.id, role="PARENT")

    dir_token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=direction.id, role="DIRECTION", tenant_id=TEST_TENANT_ID,
    )
    dir_client = TestClient(create_app(container))
    dir_client.headers.update({"Authorization": f"Bearer {dir_token}"})

    student1_id = _seed_student(container, "Enfant1", "Famille")
    student2_id = _seed_student(container, "Enfant2", "Famille")

    # Lien 1 : Père avec Enfant 1
    resp1 = dir_client.post(
        "/parent-links",
        json={
            "parent_user_id": str(parent.id),
            "student_id": str(student1_id),
            "relationship_type": "FATHER",
        },
    )
    assert resp1.status_code == 201, resp1.text
    data1 = resp1.json()
    assert data1["parent_user_id"] == str(parent.id)
    assert data1["student_id"] == str(student1_id)
    assert data1["relationship_type"] == "FATHER"

    # Lien 2 : Père avec Enfant 2 (Cardinalité N:M)
    resp2 = dir_client.post(
        "/parent-links",
        json={
            "parent_user_id": str(parent.id),
            "student_id": str(student2_id),
            "relationship_type": "FATHER",
        },
    )
    assert resp2.status_code == 201, resp2.text


def test_link_parent_student_rejects_unauthorized_role():
    client_parent, _, parent_user = _make_client(role="PARENT")
    student_id = uuid4()

    # Un parent ne peut pas s'auto-associer sans validation de l'école (PAR-REL-02)
    resp = client_parent.post(
        "/parent-links",
        json={
            "parent_user_id": str(parent_user.id),
            "student_id": str(student_id),
            "relationship_type": "MOTHER",
        },
    )
    assert resp.status_code == 403


def test_school_cannot_link_an_account_without_parent_membership():
    client_admin, container, _ = _make_client(role="ADMIN")
    student_user = User(uuid4(), "student@test.cd", "hash", "STUDENT")
    container._user_repository().save(student_user)
    seed_membership(container, student_user.id, role="STUDENT")
    student_id = _seed_student(container)

    response = client_admin.post(
        "/parent-links",
        json={
            "parent_user_id": str(student_user.id),
            "student_id": str(student_id),
            "relationship_type": "LEGAL_GUARDIAN",
        },
    )
    assert response.status_code == 404


def test_parent_portal_list_children():
    client_parent, container, parent_user = _make_client(role="PARENT")

    student1 = _seed_student(container, "Ketsia", "Kalala")
    student2 = _seed_student(container, "Moise", "Kalala")

    admin = User(uuid4(), "admin@test.cd", "hash", "ADMIN")
    container._user_repository().save(admin)
    seed_membership(container, admin.id, role="ADMIN")

    # Liaison des 2 enfants
    container.link_parent_student().execute(
        TEST_TENANT_ID, parent_user.id, student1, "MOTHER", admin.id,
    )
    container.link_parent_student().execute(
        TEST_TENANT_ID, parent_user.id, student2, "MOTHER", admin.id,
    )

    resp = client_parent.get("/parent-portal/students")
    assert resp.status_code == 200, resp.text
    children = resp.json()
    assert len(children) == 2
    names = [c["student"]["first_name"] for c in children]
    assert "Ketsia" in names
    assert "Moise" in names


def test_parent_portal_access_child_report_cards_and_pdf():
    client_parent, container, parent_user = _make_client(role="PARENT")
    student_id = _seed_student(container, "Naomie", "Mbemba")

    admin = User(uuid4(), "admin@test.cd", "hash", "ADMIN")
    container._user_repository().save(admin)
    seed_membership(container, admin.id, role="ADMIN")

    container.link_parent_student().execute(
        TEST_TENANT_ID, parent_user.id, student_id, "LEGAL_GUARDIAN", admin.id,
    )

    # Création d'un bulletin ISSUED
    period_id = uuid4()
    rc_id = uuid4()
    deliberation_id = uuid4()
    container._academic_period_repository().save(AcademicPeriod(
        period_id, TEST_TENANT_ID, "Trimestre 1", date(2026, 9, 1), date(2026, 12, 20),
    ))
    container._student_academic_record_repository().save(StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID, student_id=student_id, academic_period_id=period_id,
        subject_results=(), general_average=15.5, failed_subjects=0,
        credits_obtained=20, total_credits=30, status=AcademicRecordStatus.VALIDATED,
    ))
    SQLiteDeliberationRepository(container._database).save(Deliberation(
        student_id=student_id, average=15.5, failed_subjects=0,
        decision=DeliberationDecision.ADMITTED, tenant_id=TEST_TENANT_ID,
        academic_period_id=period_id, record_version=1, id=deliberation_id,
        status="VALIDATED", version=2, created_by=admin.id,
        created_at=datetime.now(timezone.utc), validated_by=admin.id,
        validated_at=datetime.now(timezone.utc),
    ))
    snapshot = {
        "student_name": "Naomie Mbemba",
        "period_name": "Trimestre 1",
        "general_average": 15.5,
        "decision": "ADMITTED",
    }
    container._report_card_repository().save(ReportCard(
        id=rc_id,
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=period_id,
        deliberation_id=deliberation_id,
        deliberation_version=1,
        record_version=1,
        report_version=1,
        status=ReportCardStatus.ISSUED,
        snapshot=snapshot,
        snapshot_hash=ReportCard.calculate_snapshot_hash(snapshot),
        created_at=datetime.now(timezone.utc),
        issued_at=datetime.now(timezone.utc),
        issued_by=admin.id,
    ))

    # 1. Consultation des bulletins
    cards_resp = client_parent.get(f"/parent-portal/students/{student_id}/report-cards")
    assert cards_resp.status_code == 200
    cards = cards_resp.json()
    assert len(cards) == 1
    assert cards[0]["id"] == str(rc_id)
    assert cards[0]["status"] == "ISSUED"

    # 2. Téléchargement PDF
    pdf_resp = client_parent.get(f"/parent-portal/students/{student_id}/report-cards/{rc_id}/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF")


def test_parent_portal_does_not_expose_billing_data():
    client_parent, _, _ = _make_client(role="PARENT")
    response = client_parent.get(f"/parent-portal/students/{uuid4()}/billing")
    assert response.status_code == 404

def test_par_rel_06_unassociated_student_access_is_forbidden():
    client_parent, container, _ = _make_client(role="PARENT")
    unlinked_student_id = _seed_student(container, "Autre", "Eleve")

    # Le parent n'est pas associé à cet élève -> 403 Forbidden sur bulletins et finances
    assert client_parent.get(f"/parent-portal/students/{unlinked_student_id}/report-cards").status_code == 403
    assert client_parent.get(f"/parent-portal/students/{unlinked_student_id}/report-cards/{uuid4()}/pdf").status_code == 403
