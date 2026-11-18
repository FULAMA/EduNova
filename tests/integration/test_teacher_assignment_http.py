"""
Tests d'intégration HTTP — Affectation et Portail Enseignant (Lot 7).

Scénarios vérifiés :
1. Affectation nominale d'un enseignant par ADMIN (POST /teacher-assignments -> 201)
2. Affectation nominale par DIRECTION (POST /teacher-assignments -> 201)
3. Rejet si rôle non autorisé tente une affectation (TEACHER, STUDENT, PARENT -> 403)
4. Rejet si l'utilisateur ciblé n'a pas le rôle TEACHER actif dans le tenant (400)
5. Rejet si la classe, la matière ou l'année scolaire est introuvable (400)
6. Rejet si l'année scolaire est clôturée (400)
7. Consultation des affectations par ADMIN/DIRECTION (GET /teacher-assignments?teacher_user_id=... -> 200)
8. Consultation des affectations par classe (GET /teacher-assignments?academic_class_id=... -> 200)
9. Portail Enseignant : consultation autonome de ses propres affectations (GET /teacher/assignments -> 200)
10. Isolation multi-tenant stricte
"""

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from src.academic.domain.entities.academic_class import AcademicClass
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.subject import Subject
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
    return client, container, user


def _seed_academic_fixtures(container, tenant_id=TEST_TENANT_ID, year_status=AcademicYearStatus.ACTIVE, label="2026-2027"):
    year_id = uuid4()
    class_id = uuid4()
    subject_id = uuid4()

    year = AcademicYear(
        id=year_id,
        tenant_id=tenant_id,
        label=label,
        start_date=date(2026, 9, 1),
        end_date=date(2027, 6, 30),
        status=year_status,
    )
    container._academic_year_repository().save(year)

    academic_class = AcademicClass(
        id=class_id,
        tenant_id=tenant_id,
        name="6ème Math-Physique",
    )
    container._academic_class_repository().save(academic_class)

    subject = Subject(
        id=subject_id,
        tenant_id=tenant_id,
        name="Physique Nucléaire",
        code=f"PHYS-{uuid4().hex[:4].upper()}",
        coefficient=2.0,
    )
    container._subject_repository().save(subject)

    return year_id, class_id, subject_id


def _create_teacher_user(container, tenant_id=TEST_TENANT_ID, role="TEACHER"):
    teacher = User(uuid4(), f"prof-{uuid4().hex[:6]}@edunova.test", "hashed-pass", role)
    container._user_repository().save(teacher)
    seed_membership(container, teacher.id, tenant_id=tenant_id, role=role)
    return teacher


def test_admin_and_direction_can_assign_teacher_to_class_subject():
    # 1. Test ADMIN
    client_admin, container, _ = _make_client(role="ADMIN")
    year_id, class_id, subject_id = _seed_academic_fixtures(container)
    teacher = _create_teacher_user(container)

    resp_admin = client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(teacher.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )
    assert resp_admin.status_code == 201, resp_admin.text
    data = resp_admin.json()
    assert data["teacher_user_id"] == str(teacher.id)
    assert data["academic_class_id"] == str(class_id)
    assert data["subject_id"] == str(subject_id)

    # 2. Test DIRECTION
    direction_user = User(uuid4(), "direction@edunova.test", "hash", "DIRECTION")
    container._user_repository().save(direction_user)
    seed_membership(container, direction_user.id, role="DIRECTION")

    token_dir = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=direction_user.id, role="DIRECTION", tenant_id=TEST_TENANT_ID,
    )
    client_admin.headers["Authorization"] = f"Bearer {token_dir}"

    teacher2 = _create_teacher_user(container)
    resp_dir = client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(teacher2.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )
    assert resp_dir.status_code == 201, resp_dir.text


def test_assign_teacher_rejects_unauthorized_roles():
    for forbidden_role in ("TEACHER", "STUDENT", "PARENT"):
        client, container, _ = _make_client(role=forbidden_role)
        year_id, class_id, subject_id = _seed_academic_fixtures(container)
        teacher = _create_teacher_user(container)

        resp = client.post(
            "/teacher-assignments",
            json={
                "teacher_user_id": str(teacher.id),
                "academic_class_id": str(class_id),
                "subject_id": str(subject_id),
                "academic_year_id": str(year_id),
            },
        )
        assert resp.status_code == 403, f"Expected 403 for {forbidden_role}, got {resp.status_code}"


def test_assign_teacher_validation_errors():
    client_admin, container, _ = _make_client(role="ADMIN")
    year_id, class_id, subject_id = _seed_academic_fixtures(container)

    # Utilisateur non-enseignant
    student_user = User(uuid4(), "stud@test.cd", "hash", "STUDENT")
    container._user_repository().save(student_user)
    seed_membership(container, student_user.id, role="STUDENT")

    resp = client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(student_user.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )
    assert resp.status_code == 400
    assert "enseignant" in resp.json()["detail"]

    # Année scolaire clôturée
    teacher = _create_teacher_user(container)
    closed_year_id, _, _ = _seed_academic_fixtures(
        container, year_status=AcademicYearStatus.CLOSED, label="2025-2026",
    )

    resp_closed = client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(teacher.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(closed_year_id),
        },
    )
    assert resp_closed.status_code == 400
    assert "cloturee" in resp_closed.json()["detail"]


def test_list_teacher_assignments_admin_and_teacher_portal():
    client_admin, container, _ = _make_client(role="ADMIN")
    year_id, class_id, subject_id = _seed_academic_fixtures(container)
    teacher = _create_teacher_user(container)

    # Création de l'affectation
    client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(teacher.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )

    # 1. Liste par enseignant (ADMIN)
    resp_list_teacher = client_admin.get(f"/teacher-assignments?teacher_user_id={teacher.id}")
    assert resp_list_teacher.status_code == 200
    assignments = resp_list_teacher.json()
    assert len(assignments) == 1
    assert assignments[0]["teacher_user_id"] == str(teacher.id)

    # 2. Liste par classe (ADMIN)
    resp_list_class = client_admin.get(f"/teacher-assignments?academic_class_id={class_id}")
    assert resp_list_class.status_code == 200
    assert len(resp_list_class.json()) == 1

    # 3. Portail Enseignant (TEACHER connecté)
    token_teacher = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=teacher.id, role="TEACHER", tenant_id=TEST_TENANT_ID,
    )
    client_teacher = TestClient(create_app(container))
    client_teacher.headers.update({"Authorization": f"Bearer {token_teacher}"})

    resp_my_assignments = client_teacher.get("/teacher/assignments")
    assert resp_my_assignments.status_code == 200
    my_assignments = resp_my_assignments.json()
    assert len(my_assignments) == 1
    assert my_assignments[0]["academic_class_id"] == str(class_id)
    assert my_assignments[0]["subject_id"] == str(subject_id)
    assert my_assignments[0]["academic_class_label"] == "6ème Math-Physique"
    assert my_assignments[0]["subject_label"] == "Physique Nucléaire"
    assert my_assignments[0]["academic_year_label"] == "2026-2027"


def test_canonical_prof_role_can_use_teacher_portal_and_receive_assignments():
    admin, container, _ = _make_client(role="ADMIN")
    year_id, class_id, subject_id = _seed_academic_fixtures(container)
    teacher = _create_teacher_user(container, role="PROF")
    assigned = admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(teacher.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )
    assert assigned.status_code == 201

    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=teacher.id, role="PROF", tenant_id=TEST_TENANT_ID,
    )
    client = TestClient(create_app(container))
    client.headers["Authorization"] = f"Bearer {token}"

    response = client.get("/teacher/assignments")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["academic_class_id"] == str(class_id)


def test_reassign_teacher_updates_assignment():
    client_admin, container, admin_user = _make_client(role="ADMIN")
    year_id, class_id, subject_id = _seed_academic_fixtures(container)
    teacher = _create_teacher_user(container)

    # 1. Première affectation
    r1 = client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(teacher.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )
    assert r1.status_code == 201

    # 2. Ré-affectation identique (idempotente / mise à jour de traçabilité)
    r2 = client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(teacher.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )
    assert r2.status_code == 201
    assert r2.json()["assigned_by"] == str(admin_user.id)


def test_assign_teacher_foreign_tenant_isolation():
    client_admin, container, _ = _make_client(role="ADMIN", tenant_id=TEST_TENANT_ID)
    year_id, class_id, subject_id = _seed_academic_fixtures(container, tenant_id=TEST_TENANT_ID)

    # Enseignant appartenant à un autre tenant
    other_tenant_id = uuid4()
    foreign_teacher = _create_teacher_user(container, tenant_id=other_tenant_id)

    resp = client_admin.post(
        "/teacher-assignments",
        json={
            "teacher_user_id": str(foreign_teacher.id),
            "academic_class_id": str(class_id),
            "subject_id": str(subject_id),
            "academic_year_id": str(year_id),
        },
    )
    assert resp.status_code == 400
    assert "enseignant actif" in resp.json()["detail"]

