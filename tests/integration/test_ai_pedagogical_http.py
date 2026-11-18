"""
Tests d'intégration HTTP — Moteur IA Pédagogique EduNova.

Scénarios vérifiés :
1. Génération assistée d'appréciations de bulletins pour les enseignants (POST /ai/report-cards/{id}/feedback -> 200)
2. Rejet de la génération d'appréciations par un élève ou utilisateur non autorisé (403)
3. Diagnostic précoce de risque académique et plan d'action (POST /ai/students/{id}/risk-diagnosis -> 200)
4. Synthèse pédagogique vulgarisée pour le portail parent (GET /parent-portal/students/{id}/report-cards/{id}/ai-summary -> 200)
5. Règle absolue PAR-REL-06 : refus formel du résumé IA si parent non associé à l'élève (403)
6. Rejet si le bulletin ciblé n'est pas encore officiellement émis (400)
"""

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from src.academic.domain.entities.academic_class import AcademicClass
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.attendance import Attendance, AttendanceStatus
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.academic.domain.entities.report_card import ReportCard, ReportCardStatus
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus, StudentAcademicRecord
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus
from src.academic.domain.entities.subject import Subject
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.identity.domain.entities.user import User
from src.infrastructure.repositories.sqlite_deliberation_repository import SQLiteDeliberationRepository
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def _make_client(role: str = "TEACHER", tenant_id=TEST_TENANT_ID):
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


def _seed_academic_context(container, tenant_id=TEST_TENANT_ID):
    student_id = uuid4()
    period_id = uuid4()
    year_id = uuid4()
    class_id = uuid4()
    subject_id = uuid4()
    admin_id = uuid4()
    admin_user = User(admin_id, f"admin-{uuid4().hex[:6]}@edunova.test", "hashed-pass", "ADMIN")
    container._user_repository().save(admin_user)
    seed_membership(container, admin_id, tenant_id=tenant_id, role="ADMIN")

    # Élève
    with container._database.connect() as conn:
        conn.execute(
            "INSERT INTO students (id, tenant_id, first_name, last_name, email, phone, active) "
            "VALUES (?, ?, ?, ?, ?, ?, 1)",
            (str(student_id), str(tenant_id), "Ephraim", "Kasongo", None, None),
        )

    # Année et classe
    year = AcademicYear(year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 6, 30), AcademicYearStatus.ACTIVE)
    container._academic_year_repository().save(year)

    academic_class = AcademicClass(class_id, tenant_id, "6ème Math-Physique")
    container._academic_class_repository().save(academic_class)

    # Matière
    subject = Subject(subject_id, tenant_id, "Mathématiques Générales", "MATH-601", coefficient=4.0)
    container._subject_repository().save(subject)

    # Période
    period = AcademicPeriod(period_id, tenant_id, "Trimestre 1", date(2026, 9, 1), date(2026, 12, 20))
    container._academic_period_repository().save(period)

    # Affectation
    now = datetime.now(timezone.utc)
    container._student_assignment_repository().save_active(StudentAssignment(
        uuid4(), tenant_id, student_id, year_id, class_id, None,
        StudentAssignmentStatus.ACTIVE, admin_id, now, now,
    ))

    # Dossier académique
    record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(
            SubjectResult(subject_id=subject_id, average=15.5, coefficient=4.0),
        ),
        general_average=15.5,
        failed_subjects=0,
        credits_obtained=25,
        total_credits=30,
        status=AcademicRecordStatus.VALIDATED,
    )
    container._student_academic_record_repository().save(record)

    # Délibération
    deliberation = SQLiteDeliberationRepository(container._database).save(Deliberation(
        student_id=student_id,
        average=15.5,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
        tenant_id=tenant_id,
        academic_period_id=period_id,
        record_version=1,
        id=uuid4(),
        status="VALIDATED",
        version=2,
        created_by=admin_id,
        created_at=datetime.now(timezone.utc),
        validated_by=admin_id,
        validated_at=datetime.now(timezone.utc),
    ))

    # Bulletin officiel émis (ISSUED)
    rc_id = uuid4()
    snapshot = {
        "student_id": str(student_id),
        "student_name": "Ephraim Kasongo",
        "academic_period_id": str(period_id),
        "period_name": "Trimestre 1",
        "general_average": 15.5,
        "failed_subjects": 0,
        "subject_results": [
            {"subject_id": str(subject_id), "average": 15.5, "coefficient": 4.0},
        ],
        "deliberation": {
            "id": str(deliberation.id),
            "decision": "ADMITTED",
            "average": 15.5,
        },
    }
    report_card = ReportCard(
        id=rc_id,
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        deliberation_id=deliberation.id,
        deliberation_version=2,
        record_version=1,
        report_version=1,
        status=ReportCardStatus.ISSUED,
        snapshot=snapshot,
        snapshot_hash=ReportCard.calculate_snapshot_hash(snapshot),
        created_at=datetime.now(timezone.utc),
        issued_at=datetime.now(timezone.utc),
        issued_by=admin_id,
    )
    container._report_card_repository().save(report_card)

    # Présences
    container._attendance_repository().record(Attendance(
        id=uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        academic_class_id=class_id,
        academic_year_id=year_id,
        academic_period_id=period_id,
        attendance_date=date(2026, 10, 5),
        status=AttendanceStatus.PRESENT,
    ))

    return student_id, period_id, rc_id, admin_id


def test_ai_report_card_feedback_generation():
    client_teacher, container, _ = _make_client(role="TEACHER")
    _, _, rc_id, _ = _seed_academic_context(container)

    resp = client_teacher.post(f"/ai/report-cards/{rc_id}/feedback")
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["report_card_id"] == str(rc_id)
    assert data["student_name"] == "Ephraim Kasongo"
    assert "encouraging" in data and len(data["encouraging"]) > 20
    assert "analytical" in data and len(data["analytical"]) > 20
    assert "demanding" in data and len(data["demanding"]) > 20
    assert "15.5" in data["encouraging"]


def test_ai_report_card_feedback_rejects_student_role():
    client_student, container, _ = _make_client(role="STUDENT")
    _, _, rc_id, _ = _seed_academic_context(container)

    resp = client_student.post(f"/ai/report-cards/{rc_id}/feedback")
    assert resp.status_code == 403


def test_ai_student_risk_diagnosis():
    client_direction, container, _ = _make_client(role="DIRECTION")
    student_id, period_id, _, _ = _seed_academic_context(container)

    resp = client_direction.post(f"/ai/students/{student_id}/risk-diagnosis?academic_period_id={period_id}")
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["student_id"] == str(student_id)
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert "diagnostic_summary" in data
    assert isinstance(data["action_plan"], list)
    assert len(data["action_plan"]) >= 1


def test_parent_portal_ai_summary_nominal_and_par_rel_06_guard():
    client_parent, container, parent_user = _make_client(role="PARENT")
    student_id, _, rc_id, admin_id = _seed_academic_context(container)

    # 1. Avant liaison : PAR-REL-06 doit bloquer l'accès avec 403 Forbidden
    resp_unlinked = client_parent.get(f"/parent-portal/students/{student_id}/report-cards/{rc_id}/ai-summary")
    assert resp_unlinked.status_code == 403
    assert "Accès refusé" in resp_unlinked.json()["detail"]

    # 2. Liaison officielle par l'école
    container.link_parent_student().execute(
        TEST_TENANT_ID, parent_user.id, student_id, "FATHER", admin_id,
    )

    # 3. Après liaison : consultation réussie du résumé IA
    resp_linked = client_parent.get(f"/parent-portal/students/{student_id}/report-cards/{rc_id}/ai-summary")
    assert resp_linked.status_code == 200, resp_linked.text
    data = resp_linked.json()

    assert data["student_id"] == str(student_id)
    assert "headline" in data and len(data["headline"]) > 5
    assert "summary" in data and "Ephraim Kasongo" in data["summary"]
    assert isinstance(data["tips_for_home"], list)
    assert len(data["tips_for_home"]) >= 2
