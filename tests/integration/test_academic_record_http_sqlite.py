from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.domain.entities.user import User
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = (
    "edunova-development-secret-key-"
    "32-bytes-minimum-change-in-production"
)


def create_authenticated_client(student_id):
    container = ApplicationContainer(
        database_path=":memory:"
    )
    app = create_app(container)
    client = TestClient(app)

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    container._user_repository().save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role="ADMIN",
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

    jwt_service = JwtService(secret_key=JWT_SECRET)

    token = jwt_service.create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    return client


def test_full_academic_record_http_sqlite_workflow():
    student_id = uuid4()
    academic_period_id = uuid4()
    math_subject_id = uuid4()
    physics_subject_id = uuid4()

    client = create_authenticated_client(student_id)

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
            "coefficient": 2.0,
        },
    )

    assert response.status_code == 201

    response = client.post(
        f"/academic-records/{student_id}/{academic_period_id}/subjects",
        json={
            "subject_id": str(physics_subject_id),
            "average": 12.0,
            "coefficient": 3.0,
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

