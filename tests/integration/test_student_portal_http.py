from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from src.academic.domain.entities.academic_class import AcademicClass
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.attendance import Attendance, AttendanceStatus
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus
from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus
from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def client_for(
    container: ApplicationContainer,
    user: User,
    tenant_id=TEST_TENANT_ID,
) -> TestClient:
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=tenant_id,
    )
    client = TestClient(create_app(container))
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def test_student_portal_resolves_linked_account_without_client_student_id() -> None:
    container = ApplicationContainer(database_path=":memory:")
    admin = User(uuid4(), "admin-portal@example.test", "hash", "ADMIN")
    student_user = User(uuid4(), "student-portal@example.test", "hash", "STUDENT")
    container._user_repository().save(admin)
    container._user_repository().save(student_user)
    seed_membership(container, admin.id, role="ADMIN")
    seed_membership(container, student_user.id, role="STUDENT")
    admin_client = client_for(container, admin)
    student_client = client_for(container, student_user)

    student_id, year_id, class_id = uuid4(), uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(TEST_TENANT_ID), "Eleve", "Synthetique", None, None, 1),
        )
    container._academic_year_repository().save(AcademicYear(
        year_id, TEST_TENANT_ID, "2026-2027", date(2026, 9, 1),
        date(2027, 7, 31), AcademicYearStatus.ACTIVE,
    ))
    container._academic_class_repository().save(AcademicClass(class_id, TEST_TENANT_ID, "Classe test"))
    now = datetime.now(timezone.utc)
    container._student_assignment_repository().save_active(StudentAssignment(
        uuid4(), TEST_TENANT_ID, student_id, year_id, class_id, None,
        StudentAssignmentStatus.ACTIVE, admin.id, now, now,
    ))

    link = admin_client.post("/student-links", json={
        "user_id": str(student_user.id),
        "student_id": str(student_id),
    })
    assert link.status_code == 201

    response = student_client.get(f"/me/student?student_id={uuid4()}")

    assert response.status_code == 200
    assert response.json()["student"]["id"] == str(student_id)
    assert response.json()["assignment"]["academic_year_id"] == str(year_id)


def test_student_portal_rejects_unlinked_and_non_student_accounts() -> None:
    container = ApplicationContainer(database_path=":memory:")
    unlinked = User(uuid4(), "unlinked@example.test", "hash", "STUDENT")
    teacher = User(uuid4(), "teacher@example.test", "hash", "TEACHER")
    container._user_repository().save(unlinked)
    container._user_repository().save(teacher)
    seed_membership(container, unlinked.id, role="STUDENT")
    seed_membership(container, teacher.id, role="TEACHER")

    assert client_for(container, unlinked).get("/me/student").status_code == 404
    assert client_for(container, teacher).get("/me/student").status_code == 403


def test_student_link_rejects_a_student_from_another_tenant() -> None:
    container = ApplicationContainer(database_path=":memory:")
    admin = User(uuid4(), "admin-cross-tenant@example.test", "hash", "ADMIN")
    container._user_repository().save(admin)
    seed_membership(container, admin.id, role="ADMIN")
    other_tenant_id, other_student_id = uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(other_student_id), str(other_tenant_id), "Autre", "Tenant", None, None, 1),
        )

    response = client_for(container, admin).post("/student-links", json={
        "user_id": str(uuid4()),
        "student_id": str(other_student_id),
    })

    assert response.status_code == 409
    assert "etablissement" in response.json()["detail"]


def test_student_portal_reads_only_the_linked_student_academic_record() -> None:
    container = ApplicationContainer(database_path=":memory:")
    admin = User(uuid4(), "admin-record@example.test", "hash", "ADMIN")
    student_user = User(uuid4(), "student-record@example.test", "hash", "STUDENT")
    container._user_repository().save(admin)
    container._user_repository().save(student_user)
    seed_membership(container, admin.id, role="ADMIN")
    seed_membership(container, student_user.id, role="STUDENT")
    admin_client = client_for(container, admin)
    student_client = client_for(container, student_user)

    student_id, period_id = uuid4(), uuid4()
    year_id, class_id = uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(TEST_TENANT_ID), "Eleve", "Resultats", None, None, 1),
        )
    container._academic_period_repository().save(AcademicPeriod(
        period_id, TEST_TENANT_ID, "Trimestre 1", date(2026, 9, 1),
        date(2026, 12, 20),
    ))
    container._academic_year_repository().save(AcademicYear(
        year_id, TEST_TENANT_ID, "2026-2027", date(2026, 9, 1),
        date(2027, 7, 31), AcademicYearStatus.ACTIVE,
    ))
    container._academic_class_repository().save(AcademicClass(
        class_id, TEST_TENANT_ID, "Classe presence",
    ))
    container._student_academic_record_repository().save(StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=13.2,
        failed_subjects=0,
        credits_obtained=20,
        total_credits=30,
        status=AcademicRecordStatus.VALIDATED,
    ))
    container._attendance_repository().record(Attendance(
        uuid4(), TEST_TENANT_ID, student_id, class_id, year_id, period_id,
        date(2026, 10, 20), AttendanceStatus.ABSENT, True, admin.id,
    ))
    link = admin_client.post("/student-links", json={
        "user_id": str(student_user.id),
        "student_id": str(student_id),
    })
    assert link.status_code == 201

    periods = student_client.get("/me/student/academic-periods")
    assert periods.status_code == 200
    assert periods.json() == [{"id": str(period_id), "name": "Trimestre 1"}]

    record = student_client.get(f"/me/student/academic-records/{period_id}")
    assert record.status_code == 200
    assert record.json()["student_id"] == str(student_id)
    assert record.json()["general_average"] == 13.2
    assert record.json()["status"] == "VALIDATED"

    attendance = student_client.get(f"/me/student/attendance/{period_id}")
    assert attendance.status_code == 200
    assert attendance.json()["statistics"]["absences"] == 1
    assert attendance.json()["records"][0]["status"] == "ABSENT"

    forbidden_period = student_client.get(f"/me/student/academic-records/{uuid4()}")
    assert forbidden_period.status_code == 404


def test_student_portal_cannot_read_another_tenant_or_client_selected_student() -> None:
    container = ApplicationContainer(database_path=":memory:")
    tenant_a = TEST_TENANT_ID
    tenant_b = uuid4()
    admin_a = User(uuid4(), "admin-a@example.test", "hash", "ADMIN")
    admin_b = User(uuid4(), "admin-b@example.test", "hash", "ADMIN")
    student_user_a = User(uuid4(), "student-a@example.test", "hash", "STUDENT")
    student_user_b = User(uuid4(), "student-b@example.test", "hash", "STUDENT")
    for user in (admin_a, admin_b, student_user_a, student_user_b):
        container._user_repository().save(user)
    seed_membership(container, admin_a.id, tenant_a, role="ADMIN")
    seed_membership(container, student_user_a.id, tenant_a, role="STUDENT")
    seed_membership(container, admin_b.id, tenant_b, role="ADMIN")
    seed_membership(container, student_user_b.id, tenant_b, role="STUDENT")

    student_id_a, student_id_b = uuid4(), uuid4()
    period_a, period_b = uuid4(), uuid4()
    year_a, year_b = uuid4(), uuid4()
    class_a, class_b = uuid4(), uuid4()
    with container._database.connect() as connection:
        for tenant_id, student_id, first_name in (
            (tenant_a, student_id_a, "Eleve A"),
            (tenant_b, student_id_b, "Eleve B"),
        ):
            connection.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(student_id), str(tenant_id), first_name, "Confidentiel", None, None, 1),
            )
    for tenant_id, period_id, year_id, class_id in (
        (tenant_a, period_a, year_a, class_a),
        (tenant_b, period_b, year_b, class_b),
    ):
        container._academic_period_repository().save(AcademicPeriod(
            period_id, tenant_id, "Periode protegee", date(2026, 9, 1), date(2026, 12, 20),
        ))
        container._academic_year_repository().save(AcademicYear(
            year_id, tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31),
            AcademicYearStatus.ACTIVE,
        ))
        container._academic_class_repository().save(AcademicClass(class_id, tenant_id, "Classe protegee"))
    now = datetime.now(timezone.utc)
    container._student_assignment_repository().save_active(StudentAssignment(
        uuid4(), tenant_a, student_id_a, year_a, class_a, None,
        StudentAssignmentStatus.ACTIVE, admin_a.id, now, now,
    ))
    container._student_assignment_repository().save_active(StudentAssignment(
        uuid4(), tenant_b, student_id_b, year_b, class_b, None,
        StudentAssignmentStatus.ACTIVE, admin_b.id, now, now,
    ))
    container._student_academic_record_repository().save(StudentAcademicRecord(
        tenant_id=tenant_b, student_id=student_id_b, academic_period_id=period_b,
        subject_results=(), general_average=17.5, failed_subjects=0,
        credits_obtained=30, total_credits=30, status=AcademicRecordStatus.VALIDATED,
    ))
    container._attendance_repository().record(Attendance(
        uuid4(), tenant_b, student_id_b, class_b, year_b, period_b,
        date(2026, 10, 21), AttendanceStatus.PRESENT, False, admin_b.id,
    ))
    assert client_for(container, admin_a, tenant_a).post("/student-links", json={
        "user_id": str(student_user_a.id), "student_id": str(student_id_a),
    }).status_code == 201
    assert client_for(container, admin_b, tenant_b).post("/student-links", json={
        "user_id": str(student_user_b.id), "student_id": str(student_id_b),
    }).status_code == 201

    client_a = client_for(container, student_user_a, tenant_a)
    profile = client_a.get(f"/me/student?student_id={student_id_b}&tenant_id={tenant_b}")
    assert profile.status_code == 200
    assert profile.json()["student"]["id"] == str(student_id_a)
    record = client_a.get(f"/me/student/academic-records/{period_b}")
    assert record.status_code == 404
    attendance = client_a.get(f"/me/student/attendance/{period_b}")
    assert attendance.status_code == 200
    assert attendance.json()["records"] == []
    assert str(student_id_b) not in attendance.text
    assert "Confidentiel" not in attendance.text


def test_student_portal_protects_attendance_with_role_and_token_checks() -> None:
    container = ApplicationContainer(database_path=":memory:")
    student = User(uuid4(), "student-security@example.test", "hash", "STUDENT")
    teacher = User(uuid4(), "teacher-security@example.test", "hash", "TEACHER")
    for user, role in ((student, "STUDENT"), (teacher, "TEACHER")):
        container._user_repository().save(user)
        seed_membership(container, user.id, role=role)
    period_id = uuid4()
    student_client = client_for(container, student)
    teacher_client = client_for(container, teacher)

    assert student_client.get(f"/me/student/attendance/{period_id}").status_code == 404
    assert teacher_client.get(f"/me/student/attendance/{period_id}").status_code == 403
    invalid = TestClient(create_app(container))
    invalid.headers["Authorization"] = "Bearer not-a-valid-token"
    assert invalid.get(f"/me/student/attendance/{period_id}").status_code == 401


def test_student_link_requires_existing_active_student_membership():
    container = ApplicationContainer(database_path=":memory:")
    admin = User(uuid4(), "admin-link-validation@example.test", "hash", "ADMIN")
    inactive_student = User(uuid4(), "inactive-link@example.test", "hash", "STUDENT", is_active=False)
    teacher = User(uuid4(), "teacher-link@example.test", "hash", "TEACHER")
    valid_student = User(uuid4(), "valid-link@example.test", "hash", "STUDENT")
    for user in (admin, inactive_student, teacher, valid_student):
        container._user_repository().save(user)
    seed_membership(container, admin.id, role="ADMIN")
    seed_membership(container, inactive_student.id, role="STUDENT")
    seed_membership(container, teacher.id, role="TEACHER")
    seed_membership(container, valid_student.id, role="STUDENT")

    student_id = uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(TEST_TENANT_ID), "Eleve", "Controle", None, None, 1),
        )

    client = client_for(container, admin)
    missing = client.post("/student-links", json={
        "user_id": str(uuid4()), "student_id": str(student_id),
    })
    inactive = client.post("/student-links", json={
        "user_id": str(inactive_student.id), "student_id": str(student_id),
    })
    wrong_role = client.post("/student-links", json={
        "user_id": str(teacher.id), "student_id": str(student_id),
    })

    no_membership_user = User(uuid4(), "no-membership@example.test", "hash", "STUDENT")
    container._user_repository().save(no_membership_user)
    no_membership = client.post("/student-links", json={
        "user_id": str(no_membership_user.id), "student_id": str(student_id),
    })

    valid = client.post("/student-links", json={
        "user_id": str(valid_student.id), "student_id": str(student_id),
    })

    assert missing.status_code == 409
    assert inactive.status_code == 409
    assert wrong_role.status_code == 409
    assert no_membership.status_code == 409
    assert valid.status_code == 201
