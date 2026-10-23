from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from src.academic.domain.entities.academic_class import AcademicClass
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.deliberation import Deliberation, DeliberationDecision
from src.academic.domain.entities.student_academic_record import (
    AcademicRecordStatus,
    StudentAcademicRecord,
)
from src.academic.domain.entities.student_assignment import (
    StudentAssignment,
    StudentAssignmentStatus,
)
from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.infrastructure.repositories.sqlite_deliberation_repository import SQLiteDeliberationRepository
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def client_for(role: str = "ADMIN") -> tuple[TestClient, ApplicationContainer, User]:
    container = ApplicationContainer(database_path=":memory:")
    user = User(uuid4(), f"{role.lower()}-{uuid4()}@example.test", "hash", role)
    container._user_repository().save(user)
    seed_membership(container, user.id, role=role)
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id, role=role, tenant_id=TEST_TENANT_ID,
    )
    client = TestClient(create_app(container))
    client.headers["Authorization"] = f"Bearer {token}"
    return client, container, user


def seed_school_data(container: ApplicationContainer) -> tuple[str, str]:
    student_id, class_id = uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(TEST_TENANT_ID), "Ada", "Lovelace", None, None, 1),
        )
    container._academic_class_repository().save(
        AcademicClass(class_id, TEST_TENANT_ID, "Terminale")
    )
    return str(student_id), str(class_id)


def create_year(client: TestClient) -> str:
    response = client.post(
        "/academic-years",
        json={
            "label": "2026-2027",
            "start_date": "2026-09-01",
            "end_date": "2027-07-31",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_year_lifecycle_and_assignment_activation():
    client, container, user = client_for()
    student_id, class_id = seed_school_data(container)
    year_id = create_year(client)

    assert client.get("/academic-years").json()[0]["status"] == "DRAFT"
    activated_year = client.post(f"/academic-years/{year_id}/activate")
    assert activated_year.status_code == 200
    assert activated_year.json()["status"] == "ACTIVE"

    draft = client.post(
        "/student-assignments",
        json={
            "student_id": student_id,
            "academic_year_id": year_id,
            "academic_class_id": class_id,
        },
    )
    assert draft.status_code == 201
    assignment_id = draft.json()["id"]
    assert draft.json()["status"] == "DRAFT"

    active = client.post(f"/student-assignments/{assignment_id}/activate")
    assert active.status_code == 200
    assert active.json()["status"] == "ACTIVE"
    assert active.json()["created_by"] == str(user.id)


def test_only_one_active_assignment_is_allowed():
    client, container, _ = client_for()
    student_id, class_id = seed_school_data(container)
    other_class_id = uuid4()
    container._academic_class_repository().save(
        AcademicClass(other_class_id, TEST_TENANT_ID, "Premiere")
    )
    year_id = create_year(client)
    assert client.post(f"/academic-years/{year_id}/activate").status_code == 200

    first = client.post("/student-assignments", json={
        "student_id": student_id, "academic_year_id": year_id,
        "academic_class_id": str(class_id),
    })
    assert client.post(f"/student-assignments/{first.json()['id']}/activate").status_code == 200

    second = client.post("/student-assignments", json={
        "student_id": student_id, "academic_year_id": year_id,
        "academic_class_id": str(other_class_id),
    })
    assert client.post(f"/student-assignments/{second.json()['id']}/activate").status_code == 409


def test_active_assignment_can_be_closed_and_remains_in_history():
    client, container, _ = client_for()
    student_id, class_id = seed_school_data(container)
    year_id = create_year(client)
    assert client.post(f"/academic-years/{year_id}/activate").status_code == 200

    draft = client.post("/student-assignments", json={
        "student_id": student_id,
        "academic_year_id": year_id,
        "academic_class_id": class_id,
    })
    assert draft.status_code == 201
    assignment_id = draft.json()["id"]
    assert client.post(f"/student-assignments/{assignment_id}/activate").status_code == 200

    closed = client.post(f"/student-assignments/{assignment_id}/close")

    assert closed.status_code == 200
    assert closed.json()["status"] == "CLOSED"
    history = client.get(f"/student-assignments?student_id={student_id}")
    assert history.status_code == 200
    assert [(item["id"], item["status"]) for item in history.json()] == [(assignment_id, "CLOSED")]
    assert client.post(f"/student-assignments/{assignment_id}/activate").status_code == 400


def test_assignment_close_rejects_unknown_or_other_tenant_ids():
    client, container, _ = client_for()
    student_id, class_id = seed_school_data(container)
    year_id = create_year(client)
    assert client.post(f"/academic-years/{year_id}/activate").status_code == 200
    draft = client.post("/student-assignments", json={
        "student_id": student_id,
        "academic_year_id": year_id,
        "academic_class_id": class_id,
    })
    assert draft.status_code == 201
    assert client.post(f"/student-assignments/{uuid4()}/close").status_code == 400

    other_tenant_id = uuid4()
    other_student_id = uuid4()
    other_year_id = uuid4()
    other_class_id = uuid4()
    other_assignment_id = uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(other_student_id), str(other_tenant_id), "Grace", "Hopper", None, None, 1),
        )
        connection.execute(
            "INSERT INTO academic_classes VALUES (?, ?, ?)",
            (str(other_class_id), str(other_tenant_id), "Seconde"),
        )
        connection.execute(
            "INSERT INTO academic_years VALUES (?, ?, ?, ?, ?, ?)",
            (str(other_year_id), str(other_tenant_id), "2026-2027", "2026-09-01", "2027-07-31", "ACTIVE"),
        )
        connection.execute(
            "INSERT INTO student_assignments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(other_assignment_id), str(other_tenant_id), str(other_student_id), str(other_year_id), str(other_class_id),
                None, "ACTIVE", str(uuid4()), "2026-01-01T00:00:00+00:00",
                "2026-01-01T00:00:00+00:00", None,
            ),
        )
    assert client.post(f"/student-assignments/{other_assignment_id}/close").status_code == 400


def test_assignment_and_year_reads_are_tenant_scoped():
    client, container, _ = client_for()
    student_id, class_id = seed_school_data(container)
    year_id = create_year(client)
    other_tenant_id = uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_years VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid4()), str(other_tenant_id), "2028-2029", "2028-09-01", "2029-07-31", "DRAFT"),
        )

    years = client.get("/academic-years")
    assert years.status_code == 200
    assert [year["id"] for year in years.json()] == [year_id]
    assert client.post("/student-assignments", json={
        "student_id": student_id, "academic_year_id": str(uuid4()),
        "academic_class_id": class_id,
    }).status_code == 400


def test_non_admin_cannot_manage_years_or_assignments():
    client, _, _ = client_for("TEACHER")
    assert client.get("/academic-years").status_code == 403
    assert client.post("/student-assignments", json={}).status_code == 403


def test_promotion_uses_real_route_repositories_and_is_idempotent():
    client, container, user = client_for()
    source_year_id, target_year_id = uuid4(), uuid4()
    source_class_id, target_class_id = uuid4(), uuid4()
    student_id, period_id = uuid4(), uuid4()

    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(TEST_TENANT_ID), "Ada", "Lovelace", None, None, 1),
        )

    year_repo = container._academic_year_repository()
    year_repo.save(AcademicYear(
        source_year_id, TEST_TENANT_ID, "2025-2026",
        date(2025, 9, 1), date(2026, 7, 31), AcademicYearStatus.CLOSED,
    ))
    year_repo.save(AcademicYear(
        target_year_id, TEST_TENANT_ID, "2026-2027",
        date(2026, 9, 1), date(2027, 7, 31), AcademicYearStatus.ACTIVE,
    ))
    class_repo = container._academic_class_repository()
    class_repo.save(AcademicClass(source_class_id, TEST_TENANT_ID, "Ancienne classe"))
    class_repo.save(AcademicClass(target_class_id, TEST_TENANT_ID, "Nouvelle classe"))

    now = datetime.now(timezone.utc)
    assignment_repo = container._student_assignment_repository()
    source_assignment = StudentAssignment(
        uuid4(), TEST_TENANT_ID, student_id, source_year_id, source_class_id,
        None, StudentAssignmentStatus.ACTIVE, user.id, now, now,
    )
    assignment_repo.save_active(source_assignment)

    container._academic_period_repository().save(AcademicPeriod(
        period_id, TEST_TENANT_ID, "Semestre 2", date(2026, 1, 1),
        date(2026, 7, 31), source_year_id,
    ))
    container._student_academic_record_repository().save(StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=14,
        failed_subjects=0,
        credits_obtained=1,
        total_credits=1,
        status=AcademicRecordStatus.VALIDATED,
    ))
    deliberation = SQLiteDeliberationRepository(container._database).save(Deliberation(
        student_id=student_id,
        average=14,
        failed_subjects=0,
        decision=DeliberationDecision.ADMITTED,
        tenant_id=TEST_TENANT_ID,
        academic_period_id=period_id,
        record_version=1,
        status="VALIDATED",
        created_by=user.id,
    ))

    payload = {
        "source_assignment_id": str(source_assignment.id),
        "deliberation_id": str(deliberation.id),
        "target_year_id": str(target_year_id),
        "target_class_id": str(target_class_id),
    }
    first = client.post("/student-assignments/promote", json=payload)
    second = client.post("/student-assignments/promote", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    history = assignment_repo.list_by_student(student_id, TEST_TENANT_ID)
    assert len(history) == 2
    assert any(item.id == source_assignment.id and item.status is StudentAssignmentStatus.ACTIVE for item in history)
    assert sum(item.academic_year_id == target_year_id for item in history) == 1


def test_promotion_rejects_an_assignment_from_another_tenant():
    client, container, user = client_for()
    other_tenant_id = uuid4()
    other_student_id, other_year_id, other_class_id = uuid4(), uuid4(), uuid4()
    now = datetime.now(timezone.utc).isoformat()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(other_student_id), str(other_tenant_id), "Grace", "Hopper", None, None, 1),
        )
        connection.execute(
            "INSERT INTO academic_years VALUES (?, ?, ?, ?, ?, ?)",
            (str(other_year_id), str(other_tenant_id), "2026-2027", "2026-09-01", "2027-07-31", "ACTIVE"),
        )
        connection.execute(
            "INSERT INTO academic_classes VALUES (?, ?, ?)",
            (str(other_class_id), str(other_tenant_id), "Autre classe"),
        )
        other_assignment_id = uuid4()
        connection.execute(
            "INSERT INTO student_assignments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(other_assignment_id), str(other_tenant_id), str(other_student_id), str(other_year_id), str(other_class_id), None, "ACTIVE", str(user.id), now, now, None),
        )

    response = client.post("/student-assignments/promote", json={
        "source_assignment_id": str(other_assignment_id),
        "deliberation_id": str(uuid4()),
        "target_year_id": str(uuid4()),
        "target_class_id": str(uuid4()),
    })

    assert response.status_code == 409
    assert "introuvable" in response.json()["detail"]
