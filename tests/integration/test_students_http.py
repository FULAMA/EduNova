from uuid import uuid4

from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def create_client(role: str = "ADMIN") -> tuple[TestClient, ApplicationContainer, User]:
    container = ApplicationContainer(database_path=":memory:")
    user = User(
        id=uuid4(),
        email=f"{role.lower()}-{uuid4()}@edunova.com",
        password_hash="hashed-password",
        role=role,
    )
    container._user_repository().save(user)
    seed_membership(container, user.id, role=role)

    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role=role,
        tenant_id=TEST_TENANT_ID,
    )
    client = TestClient(create_app(container))
    client.headers["Authorization"] = f"Bearer {token}"
    return client, container, user


def insert_student(container: ApplicationContainer, tenant_id=TEST_TENANT_ID):
    student_id = uuid4()
    with container._database.connect() as connection:
        connection.execute(
            """
            INSERT INTO students (
                id, tenant_id, first_name, last_name, email, phone, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_id),
                str(tenant_id),
                "Ada",
                "Lovelace",
                "ada@example.test",
                None,
                1,
            ),
        )
    return student_id


def test_admin_lists_only_students_from_active_tenant():
    client, container, _ = create_client()
    student_id = insert_student(container)
    insert_student(container, uuid4())

    response = client.get("/students")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(student_id),
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.test",
            "active": True,
        }
    ]


def test_empty_tenant_returns_empty_list():
    client, _, _ = create_client()

    response = client.get("/students")

    assert response.status_code == 200
    assert response.json() == []


def test_non_admin_cannot_list_students():
    client, container, _ = create_client(role="TEACHER")
    insert_student(container)

    response = client.get("/students")

    assert response.status_code == 403
    assert response.json()["detail"] == "Acces interdit."


def test_inactive_membership_cannot_list_students():
    client, container, user = create_client()
    with container._database.connect() as connection:
        connection.execute(
            "UPDATE memberships SET active = 0 WHERE user_id = ?",
            (str(user.id),),
        )
    insert_student(container)

    response = client.get("/students")

    assert response.status_code == 403
    assert "students" not in response.text


def test_tenant_from_membership_context_overrides_jwt_tenant_claim():
    client, container, user = create_client()
    other_tenant_id = uuid4()
    insert_student(container)
    other_student_id = insert_student(container, other_tenant_id)

    # The user has no active membership in the tenant claimed by this token.
    token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=other_tenant_id,
    )
    client.headers["Authorization"] = f"Bearer {token}"

    response = client.get("/students")

    assert response.status_code == 403
    assert str(other_student_id) not in response.text


def test_student_list_requires_authentication():
    container = ApplicationContainer(database_path=":memory:")
    client = TestClient(create_app(container))

    response = client.get("/students")

    assert response.status_code == 401


def test_admin_gets_student_detail_from_active_tenant():
    client, container, _ = create_client()
    student_id = insert_student(container)

    response = client.get(f"/students/{student_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(student_id),
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.test",
        "active": True,
    }


def test_missing_or_cross_tenant_student_is_indistinguishable():
    client, container, _ = create_client()
    other_student_id = insert_student(container, uuid4())

    cross_tenant_response = client.get(f"/students/{other_student_id}")
    missing_response = client.get(f"/students/{uuid4()}")

    assert cross_tenant_response.status_code == missing_response.status_code == 404
    assert cross_tenant_response.json() == missing_response.json() == {
        "detail": "Eleve introuvable."
    }


def test_detail_rejects_malformed_student_id():
    client, _, _ = create_client()

    response = client.get("/students/not-a-uuid")

    assert response.status_code == 422


def test_non_admin_cannot_get_student_detail():
    client, container, _ = create_client(role="TEACHER")
    student_id = insert_student(container)

    response = client.get(f"/students/{student_id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Acces interdit."


def test_inactive_membership_cannot_get_student_detail():
    client, container, user = create_client()
    student_id = insert_student(container)
    with container._database.connect() as connection:
        connection.execute(
            "UPDATE memberships SET active = 0 WHERE user_id = ?",
            (str(user.id),),
        )

    response = client.get(f"/students/{student_id}")

    assert response.status_code == 403
    assert "Ada" not in response.text


def test_student_detail_requires_authentication():
    container = ApplicationContainer(database_path=":memory:")
    client = TestClient(create_app(container))

    response = client.get(f"/students/{uuid4()}")

    assert response.status_code == 401
