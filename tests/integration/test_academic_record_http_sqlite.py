from uuid import uuid4

from datetime import date, datetime, timezone
from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership
from src.academic.domain.events.subject_result_added import SubjectResultAdded
from src.shared.application.events.event_handler import EventHandler
from src.shared.domain.events.domain_event import DomainEvent
from src.academic.domain.entities.academic_year import AcademicYear, AcademicYearStatus
from src.academic.domain.entities.academic_period import AcademicPeriod
from src.academic.domain.entities.academic_class import AcademicClass
from src.academic.domain.entities.class_subject import ClassSubject
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus
from src.academic.domain.entities.subject import Subject
from src.infrastructure.repositories.sqlite_academic_year_repository import SQLiteAcademicYearRepository
from src.infrastructure.repositories.sqlite_academic_period_repository import SQLiteAcademicPeriodRepository
from src.infrastructure.repositories.sqlite_academic_class_repository import SQLiteAcademicClassRepository
from src.infrastructure.repositories.sqlite_class_subject_repository import SQLiteClassSubjectRepository
from src.infrastructure.repositories.sqlite_student_assignment_repository import SQLiteStudentAssignmentRepository
from src.infrastructure.repositories.sqlite_subject_repository import SQLiteSubjectRepository




def seed_eligible_context(container, user_id, student_id, period_id, subject_count=2):
    year_id, class_id = uuid4(), uuid4()
    SQLiteAcademicYearRepository(container._database).save(AcademicYear(
        year_id, TEST_TENANT_ID, "2026-2027", date(2026, 9, 1), date(2027, 6, 30), AcademicYearStatus.ACTIVE,
    ))
    SQLiteAcademicClassRepository(container._database).save(AcademicClass(class_id, TEST_TENANT_ID, "6e"))
    SQLiteAcademicPeriodRepository(container._database).save(AcademicPeriod(
        period_id, TEST_TENANT_ID, "Trimestre 1", date(2026, 9, 1), date(2026, 12, 20), year_id,
    ))
    now = datetime.now(timezone.utc)
    SQLiteStudentAssignmentRepository(container._database).save(StudentAssignment(
        uuid4(), TEST_TENANT_ID, student_id, year_id, class_id, None,
        StudentAssignmentStatus.ACTIVE, user_id, now, now,
    ))
    subjects = []
    subject_repository = SQLiteSubjectRepository(container._database)
    class_subject_repository = SQLiteClassSubjectRepository(container._database)
    for index in range(subject_count):
        subject = Subject(uuid4(), TEST_TENANT_ID, f"Matiere {index + 1}", f"T{uuid4().hex[:8]}", 1)
        subject_repository.save(subject)
        class_subject_repository.save(ClassSubject(
            uuid4(), TEST_TENANT_ID, class_id, subject.id, float(index + 2), active=True,
        ))
        subjects.append(subject)
    container._test_subjects = tuple(subjects)
    return tuple(subjects)


def create_authenticated_client(student_id, role="ADMIN", active=True, raise_server_exceptions=True, period_id=None, subject_count=2):
    container = ApplicationContainer(
        database_path=":memory:"
    )
    app = create_app(container)
    client = TestClient(app, raise_server_exceptions=raise_server_exceptions)
    app.state.container = container

    user = User(
        id=uuid4(),
        email=f"{role.lower()}-{uuid4()}@edunova.com",
        password_hash="hashed-password",
        role=role,
        is_active=active,
    )

    container._user_repository().save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role=role,
    )

    with container._database.connect() as connection:
        connection.execute(
            """
            INSERT INTO students (
                id,
                tenant_id,
                first_name,
                last_name,
                email,
                phone,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_id),
                str(TEST_TENANT_ID),
                "Test",
                "Student",
                None,
                None,
                1,
            ),
        )

    if period_id is not None and role == "ADMIN":
        seed_eligible_context(container, user.id, student_id, period_id, subject_count)

    jwt_service = JwtService(secret_key=TEST_JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=user.id,
        role=role,
        tenant_id=TEST_TENANT_ID,
    )

    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    return client


def test_academic_record_writes_require_admin_role():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(student_id, role="TEACHER")

    create_response = client.post(
        "/academic-records",
        json={"student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 30.0},
    )
    add_response = client.post(
        f"/academic-records/{student_id}/{period_id}/subjects",
        json={"subject_id": str(uuid4()), "average": 15.0},
    )

    assert create_response.status_code == 403
    assert add_response.status_code == 403


def test_academic_record_writes_reject_inactive_account_with_valid_token():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(student_id, active=False)

    create_response = client.post(
        "/academic-records",
        json={"student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 30.0},
    )
    add_response = client.post(
        f"/academic-records/{student_id}/{period_id}/subjects",
        json={"subject_id": str(uuid4()), "average": 15.0},
    )

    assert create_response.status_code == 401
    assert create_response.json()["detail"] == "Compte desactive."
    assert add_response.status_code == 401
    assert add_response.json()["detail"] == "Compte desactive."


def test_academic_record_api_rejects_non_finite_numeric_values():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)

    create_response = client.post(
        "/academic-records",
        json={"student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": "Infinity"},
    )
    add_response = client.post(
        f"/academic-records/{student_id}/{period_id}/subjects",
        json={"subject_id": str(uuid4()), "average": "NaN"},
    )

    assert create_response.status_code == 422
    assert add_response.status_code == 422


def test_event_handler_failure_returns_error_after_record_result_is_persisted():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(
        student_id, raise_server_exceptions=False, period_id=period_id
    )
    container = client.app.state.container

    assert client.post(
        "/academic-records",
        json={"student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 30.0},
    ).status_code == 201

    class FailingHandler(EventHandler):
        def handle(self, event: DomainEvent) -> None:
            assert isinstance(event, SubjectResultAdded)
            raise RuntimeError("consumer unavailable")

    container._event_dispatcher.register(SubjectResultAdded, FailingHandler())
    subject_id = container._test_subjects[0].id
    response = client.post(
        f"/academic-records/{student_id}/{period_id}/subjects",
        json={"subject_id": str(subject_id), "average": 15.0},
    )

    persisted = container._student_academic_record_repository().find_by_student_and_period(
        student_id, period_id, TEST_TENANT_ID
    )
    assert response.status_code == 500
    assert persisted is not None
    assert [result.subject_id for result in persisted.subject_results] == [subject_id]


def test_full_academic_record_http_sqlite_workflow():
    student_id = uuid4()
    academic_period_id = uuid4()
    client = create_authenticated_client(student_id, period_id=academic_period_id)
    math_subject_id, physics_subject_id = (subject.id for subject in client.app.state.container._test_subjects)

    response = client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(academic_period_id),
            "total_credits": 30.0,
        },
    )

    assert response.status_code == 201

    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(math_subject_id),
            "average": 15.0,
        },
    )

    assert response.status_code == 201

    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(physics_subject_id),
            "average": 12.0,
        },
    )

    assert response.status_code == 201

    response = client.get(
        f"/academic-records/{student_id}/{academic_period_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["student_id"] == str(student_id)
    assert data["academic_period_id"] == str(academic_period_id)
    assert data["total_credits"] == 30.0
    assert len(data["subject_results"]) == 2


def test_duplicate_academic_record_create_keeps_http_conflict_contract():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)
    payload = {
        "student_id": str(student_id),
        "academic_period_id": str(period_id),
        "total_credits": 30.0,
    }

    assert client.post("/academic-records", json=payload).status_code == 201
    duplicate = client.post("/academic-records", json=payload)

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Academic record already exists"




def test_academic_record_read_returns_real_subject_values_without_mutation():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)
    subject_id = client.app.state.container._test_subjects[0].id
    assert client.post("/academic-records", json={"student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 24.0}).status_code == 201
    assert client.post(f"/academic-records/{student_id}/{period_id}/subjects", json={"subject_id": str(subject_id), "average": 14.5}).status_code == 201

    before = client.get(f"/academic-records/{student_id}/{period_id}").json()
    after = client.get(f"/academic-records/{student_id}/{period_id}").json()

    assert before == after
    assert before["general_average"] == 14.5
    assert before["subject_results"][0]["average"] == 14.5
    assert before["subject_results"][0]["coefficient"] == 2.0


def test_academic_record_period_list_only_returns_records_for_student():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)
    assert client.post("/academic-records", json={"student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 24.0}).status_code == 201

    response = client.get(f"/academic-records/students/{student_id}/periods")

    assert response.status_code == 200
    assert response.json() == [{"id": str(period_id), "name": "Trimestre 1"}]
    assert client.get(f"/academic-records/students/{uuid4()}/periods").json() == []


def test_academic_record_read_rejects_unknown_period():
    student_id = uuid4()
    client = create_authenticated_client(student_id)
    response = client.get(f"/academic-records/{student_id}/{uuid4()}")
    assert response.status_code == 404


def test_academic_record_read_rejects_teacher_role():
    student_id = uuid4()
    client = create_authenticated_client(student_id, role="TEACHER")
    response = client.get(f"/academic-records/{student_id}/{uuid4()}")
    assert response.status_code == 403


def test_academic_record_validation_correction_and_version_conflict():
    student_id = uuid4()
    period_id = uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)

    assert client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "total_credits": 30.0,
        },
    ).status_code == 201

    validated = client.post(
        f"/academic-records/{student_id}/{period_id}/validate",
        json={"expected_version": 1},
    )
    assert validated.status_code == 200
    assert validated.json()["status"] == "VALIDATED"
    assert validated.json()["version"] == 2

    conflict = client.post(
        f"/academic-records/{student_id}/{period_id}/correct",
        json={
            "expected_version": 0,
            "reason": "Correction de test",
            "general_average": 16.0,
            "failed_subjects": 0,
            "credits_obtained": 30.0,
        },
    )
    assert conflict.status_code == 409

    corrected = client.post(
        f"/academic-records/{student_id}/{period_id}/correct",
        json={
            "expected_version": 2,
            "reason": "Correction de test",
            "general_average": 16.0,
            "failed_subjects": 0,
            "credits_obtained": 30.0,
        },
    )
    assert corrected.status_code == 200
    assert corrected.json()["status"] == "VALIDATED"
    assert corrected.json()["version"] == 3

    history = client.get(
        f"/academic-records/{student_id}/{period_id}/history"
    )
    assert history.status_code == 200
    assert history.json()[-1]["operation"] == "CORRECTED"
    assert history.json()[-1]["reason"] == "Correction de test"


def test_http_correction_ignores_forged_aggregate_values():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)
    subjects = client.app.state.container._test_subjects

    assert client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "total_credits": 30.0,
        },
    ).status_code == 201

    for subject, average in zip(subjects, (14.0, 8.0)):
        assert client.post(
            f"/academic-records/{student_id}/{period_id}/subjects",
            json={"subject_id": str(subject.id), "average": average},
        ).status_code == 201

    validated = client.post(
        f"/academic-records/{student_id}/{period_id}/validate",
        json={"expected_version": 3},
    )
    assert validated.status_code == 200

    corrected = client.post(
        f"/academic-records/{student_id}/{period_id}/correct",
        json={
            "expected_version": 4,
            "reason": "Correction de test",
            "general_average": 20.0,
            "failed_subjects": 99,
            "credits_obtained": 30.0,
        },
    )

    assert corrected.status_code == 200
    assert corrected.json()["general_average"] == 10.4
    assert corrected.json()["failed_subjects"] == 0
    assert corrected.json()["credits_obtained"] == 0.0


def test_academic_record_history_returns_404_when_record_does_not_exist():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id)

    response = client.get(
        f"/academic-records/{student_id}/{period_id}/history"
    )

    assert response.status_code == 404


def test_academic_record_history_requires_admin_role():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id, role="TEACHER")

    response = client.get(
        f"/academic-records/{student_id}/{period_id}/history"
    )

    assert response.status_code == 403


def test_academic_record_history_hides_corrupt_storage_error():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)

    assert client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "total_credits": 30.0,
        },
    ).status_code == 201
    assert client.post(
        f"/academic-records/{student_id}/{period_id}/validate",
        json={"expected_version": 1},
    ).status_code == 200

    database = client.app.state.container._database
    with database.connect() as connection:
        connection.execute(
            "UPDATE student_academic_record_history SET snapshot_json = ?",
            ("{invalid-json",),
        )

    response = client.get(f"/academic-records/{student_id}/{period_id}/history")

    assert response.status_code == 503
    assert response.json()["detail"] == "L'historique du dossier est temporairement indisponible."
    assert "invalid-json" not in response.text


def test_academic_record_history_returns_service_unavailable_when_storage_is_missing():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)

    assert client.post(
        "/academic-records",
        json={
            "student_id": str(student_id),
            "academic_period_id": str(period_id),
            "total_credits": 30.0,
        },
    ).status_code == 201
    assert client.post(
        f"/academic-records/{student_id}/{period_id}/validate",
        json={"expected_version": 1},
    ).status_code == 200

    database = client.app.state.container._database
    with database.connect() as connection:
        connection.execute("DROP TABLE student_academic_record_history")

    response = client.get(f"/academic-records/{student_id}/{period_id}/history")

    assert response.status_code == 503
    assert response.json()["detail"] == "L'historique du dossier est temporairement indisponible."


def test_deliberation_returns_404_when_record_does_not_exist():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id)

    response = client.get(
        f"/academic-records/{student_id}/{period_id}/deliberation"
    )

    assert response.status_code == 404


def test_available_periods_and_subject_coefficients_come_from_eligible_assignments():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)
    container = client.app.state.container

    available = client.get(f"/academic-records/students/{student_id}/available-periods")
    assert available.status_code == 200
    assert available.json() == [{
        "id": str(period_id), "name": "Trimestre 1",
        "academic_year_id": str(container._academic_year_repository().list_by_tenant(TEST_TENANT_ID)[0].id),
        "academic_year_label": "2026-2027",
        "has_record": False,
    }]

    subjects = client.get(f"/academic-records/students/{student_id}/periods/{period_id}/subjects")
    assert subjects.status_code == 200
    assert [row["coefficient"] for row in subjects.json()] == [2.0, 3.0]

    assert client.post("/academic-records", json={
        "student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 30,
    }).status_code == 201
    forged = client.post(f"/academic-records/{student_id}/{period_id}/subjects", json={
        "subject_id": str(container._test_subjects[0].id), "average": 15, "coefficient": 999,
    })
    assert forged.status_code == 422
    added = client.post(f"/academic-records/{student_id}/{period_id}/subjects", json={
        "subject_id": str(container._test_subjects[0].id), "average": 15,
    })
    assert added.status_code == 201
    assert added.json()["coefficient"] == 2.0
    assert client.get(f"/academic-records/students/{student_id}/available-periods").json()[0]["has_record"] is True


def test_inactive_class_subject_is_not_available_or_writable():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id, period_id=period_id)
    container = client.app.state.container
    subject_id = container._test_subjects[0].id
    with container._database.connect() as connection:
        connection.execute("UPDATE class_subjects SET active = 0 WHERE subject_id = ?", (str(subject_id),))
    assert client.get(f"/academic-records/students/{student_id}/periods/{period_id}/subjects").json() == [
        {"id": str(container._test_subjects[1].id), "name": container._test_subjects[1].name, "coefficient": 3.0}
    ]
    assert client.post("/academic-records", json={
        "student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 30,
    }).status_code == 201
    rejected = client.post(f"/academic-records/{student_id}/{period_id}/subjects", json={
        "subject_id": str(subject_id), "average": 15,
    })
    assert rejected.status_code == 404


def test_unlinked_historical_period_remains_visible_but_cannot_start_a_new_record():
    student_id, period_id = uuid4(), uuid4()
    client = create_authenticated_client(student_id, period_id=uuid4())
    container = client.app.state.container
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
            (str(period_id), str(TEST_TENANT_ID), "Ancienne periode", "2025-09-01", "2025-12-20"),
        )
    response = client.post("/academic-records", json={
        "student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 30,
    })
    assert response.status_code == 400
    assert "historique" in response.json()["detail"]
    assert all(row["id"] != str(period_id) for row in client.get(
        f"/academic-records/students/{student_id}/available-periods"
    ).json())
