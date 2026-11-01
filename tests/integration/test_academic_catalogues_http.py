from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership
from src.academic.domain.entities.academic_class import AcademicClass
from src.infrastructure.repositories.sqlite_academic_class_repository import SQLiteAcademicClassRepository


def client_for(role: str = "ADMIN"):
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


def test_admin_manages_subjects_and_reads_tenant_periods():
    client, container, _ = client_for()
    other_tenant, period_id = uuid4(), uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
            (str(period_id), str(TEST_TENANT_ID), "Trimestre 1", "2026-09-01", "2026-12-20"),
        )
        connection.execute(
            "INSERT INTO academic_periods (id, tenant_id, name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
            (str(uuid4()), str(other_tenant), "Secret period", "2026-09-01", "2026-12-20"),
        )

    created = client.post("/academic-catalogues/subjects", json={
        "name": "Mathématiques", "code": "MATH", "coefficient": 2,
    })
    assert created.status_code == 201
    subject_id = created.json()["id"]
    assert client.get("/academic-catalogues/subjects?search=math").json()[0]["name"] == "Mathématiques"
    assert client.get("/academic-catalogues/periods").json() == [{
        "id": str(period_id), "name": "Trimestre 1",
        "start_date": "2026-09-01", "end_date": "2026-12-20",
    }]

    changed = client.put(f"/academic-catalogues/subjects/{subject_id}", json={
        "name": "Mathématiques générales", "code": "MATH",
    })
    assert changed.status_code == 200
    assert changed.json()["coefficient"] == 2
    assert client.get("/academic-catalogues/subjects").json()[0]["name"] == "Mathématiques générales"
    duplicate = client.post("/academic-catalogues/subjects", json={
        "name": "Matière dupliquée", "code": "MATH", "coefficient": 1,
    })
    assert duplicate.status_code == 409


def test_catalogues_require_admin_active_membership_and_tenant_scope():
    teacher_client, _, _ = client_for("TEACHER")
    assert teacher_client.get("/academic-catalogues/subjects").status_code == 403
    assert teacher_client.post("/academic-catalogues/subjects", json={
        "name": "Maths", "code": "MATH", "coefficient": 2,
    }).status_code == 403

    client, container, user = client_for()
    with container._database.connect() as connection:
        connection.execute("UPDATE memberships SET active = 0 WHERE user_id = ?", (str(user.id),))
    assert client.get("/academic-catalogues/periods").status_code == 403


def test_catalogue_creation_rejects_invalid_fields():
    client, _, _ = client_for()
    assert client.post("/academic-catalogues/subjects", json={
        "name": " ", "code": "MATH", "coefficient": 0,
    }).status_code == 422


def create_calendar(client, name: str = "Calendrier principal"):
    response = client.post("/academic-calendars", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_period_creation_requires_tenant_year_and_dates_inside_school_year():
    client, _, _ = client_for()
    calendar_id = create_calendar(client)
    year = client.post("/academic-years", json={
        "label": "2026-2027", "start_date": "2026-09-01", "end_date": "2027-06-30",
    })
    assert year.status_code == 201
    period = client.post("/academic-catalogues/periods", json={
        "academic_year_id": year.json()["id"], "academic_calendar_id": calendar_id, "name": "Trimestre 1",
        "start_date": "2026-09-01", "end_date": "2026-12-20",
    })
    assert period.status_code == 201
    assert period.json()["academic_year_id"] == year.json()["id"]
    assert client.post("/academic-catalogues/periods", json={
        "academic_year_id": str(uuid4()), "academic_calendar_id": calendar_id, "name": "Autre tenant",
        "start_date": "2026-09-01", "end_date": "2026-12-20",
    }).status_code == 400
    assert client.post("/academic-catalogues/periods", json={
        "academic_year_id": year.json()["id"], "academic_calendar_id": calendar_id, "name": "Hors dates",
        "start_date": "2025-09-01", "end_date": "2025-12-20",
    }).status_code == 400


def test_academic_record_returns_real_subject_and_period_labels():
    client, container, _ = client_for()
    student_id, period_id = uuid4(), uuid4()
    subject = client.post("/academic-catalogues/subjects", json={
        "name": "Physique", "code": "PHYS", "coefficient": 3,
    }).json()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(student_id), str(TEST_TENANT_ID), "Ada", "Lovelace", None, None, 1),
        )
    year = client.post("/academic-years", json={
        "label": "2026-2027", "start_date": "2026-09-01", "end_date": "2027-06-30",
    }).json()
    calendar_id = create_calendar(client)
    assert client.post(f"/academic-years/{year['id']}/activate").status_code == 200
    class_id = uuid4()
    SQLiteAcademicClassRepository(container._database).save(AcademicClass(class_id, TEST_TENANT_ID, "6e"))
    draft = client.post("/student-assignments", json={
        "student_id": str(student_id), "academic_year_id": year["id"], "academic_class_id": str(class_id),
    })
    assert draft.status_code == 201
    assert client.post(f"/student-assignments/{draft.json()['id']}/activate").status_code == 200
    created_period = client.post("/academic-catalogues/periods", json={
        "academic_year_id": year["id"], "academic_calendar_id": calendar_id, "name": "Semestre 1",
        "start_date": "2026-09-01", "end_date": "2027-01-31",
    })
    assert created_period.status_code == 201
    period_id = created_period.json()["id"]
    assert client.post(f"/classes/{class_id}/subjects", json={"subject_id": subject["id"], "coefficient": 3}).status_code == 201
    assert client.post("/academic-records", json={
        "student_id": str(student_id), "academic_period_id": str(period_id), "total_credits": 30,
    }).status_code == 201
    assert client.post(f"/academic-records/{student_id}/{period_id}/subjects", json={
        "subject_id": subject["id"], "average": 15,
    }).status_code == 201

    record = client.get(f"/academic-records/{student_id}/{period_id}").json()
    periods = client.get(f"/academic-records/students/{student_id}/periods").json()
    assert record["academic_period_name"] == "Semestre 1"
    assert record["subject_results"][0]["subject_name"] == "Physique"
    assert periods == [{"id": str(period_id), "name": "Semestre 1"}]


def test_period_overlap_is_rejected_within_calendar_but_allowed_between_calendars():
    client, _, _ = client_for()
    year = client.post("/academic-years", json={
        "label": "2026-2027", "start_date": "2026-09-01", "end_date": "2027-06-30",
    }).json()
    calendar_a = create_calendar(client, "Calendrier primaire")
    calendar_b = create_calendar(client, "Calendrier secondaire")

    first = client.post("/academic-catalogues/periods", json={
        "academic_year_id": year["id"], "academic_calendar_id": calendar_a,
        "name": "Période A1", "start_date": "2026-09-01", "end_date": "2026-12-20",
    })
    assert first.status_code == 201, first.text

    overlapping_same_calendar = client.post("/academic-catalogues/periods", json={
        "academic_year_id": year["id"], "academic_calendar_id": calendar_a,
        "name": "Période A2", "start_date": "2026-12-20", "end_date": "2027-02-01",
    })
    assert overlapping_same_calendar.status_code == 400

    overlapping_other_calendar = client.post("/academic-catalogues/periods", json={
        "academic_year_id": year["id"], "academic_calendar_id": calendar_b,
        "name": "Période B1", "start_date": "2026-10-01", "end_date": "2027-01-15",
    })
    assert overlapping_other_calendar.status_code == 201, overlapping_other_calendar.text


def test_academic_calendar_is_tenant_scoped_and_name_is_unique_case_insensitively():
    client, _, _ = client_for()
    created = client.post("/academic-calendars", json={"name": "Primaire"})
    assert created.status_code == 201
    assert client.get("/academic-calendars").status_code == 200
    assert len(client.get("/academic-calendars").json()) == 1
    duplicate = client.post("/academic-calendars", json={"name": "primaire"})
    assert duplicate.status_code == 409
    assert client.post("/academic-calendars", json={"name": " "}).status_code == 422
