from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.domain.entities.academic_class import AcademicClass
from src.domain.entities.academic_option import AcademicOption
from src.domain.entities.class_option import ClassOption
from src.domain.entities.subject import Subject
from src.domain.entities.user import User
from src.infrastructure.repositories.sqlite_academic_class_repository import (
    SQLiteAcademicClassRepository,
)
from src.infrastructure.repositories.sqlite_academic_option_repository import (
    SQLiteAcademicOptionRepository,
)
from src.infrastructure.repositories.sqlite_class_option_repository import (
    SQLiteClassOptionRepository,
)
from src.infrastructure.repositories.sqlite_subject_repository import (
    SQLiteSubjectRepository,
)
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = (
    "edunova-development-secret-key-"
    "32-bytes-minimum-change-in-production"
)


def create_test_environment():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    academic_class_repository = SQLiteAcademicClassRepository(
        container._database
    )

    subject_repository = SQLiteSubjectRepository(
        container._database
    )

    academic_option_repository = SQLiteAcademicOptionRepository(
        container._database
    )

    class_option_repository = SQLiteClassOptionRepository(
        container._database
    )

    academic_class = AcademicClass(
        id=uuid4(),
        tenant_id=TEST_TENANT_ID,
        name="6e Informatique",
    )

    subject = Subject(
        id=uuid4(),
        tenant_id=TEST_TENANT_ID,
        name="Algorithmique",
        code="ALGO",
        coefficient=3,
    )

    option = AcademicOption(
        id=uuid4(),
        tenant_id=TEST_TENANT_ID,
        name="Informatique",
        code="INFO",
    )

    class_option = ClassOption(
        id=uuid4(),
        tenant_id=TEST_TENANT_ID,
        academic_class_id=academic_class.id,
        academic_option_id=option.id,
    )

    academic_class_repository.save(academic_class)
    subject_repository.save(subject)
    academic_option_repository.save(option)
    class_option_repository.save(class_option)

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

    jwt_service = JwtService(
        secret_key=JWT_SECRET
    )

    token = jwt_service.create_access_token(
        user_id=user.id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    app = create_app(container)
    client = TestClient(app)

    client.headers.update(
        {
            "Authorization": f"Bearer {token}"
        }
    )

    return (
        client,
        academic_class,
        subject,
        option,
    )


def test_assign_subject_http_sqlite_success():
    client, academic_class, subject, _ = create_test_environment()

    response = client.post(
        f"/classes/{academic_class.id}/subjects",
        json={
            "subject_id": str(subject.id),
            "coefficient": 3,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["academic_class_id"] == str(
        academic_class.id
    )

    assert data["subject_id"] == str(
        subject.id
    )

    assert data["coefficient"] == 3

    assert data["academic_option_id"] is None
    assert data["active"] is True


def test_assign_subject_http_sqlite_duplicate_returns_409():
    client, academic_class, subject, _ = create_test_environment()

    first_response = client.post(
        f"/classes/{academic_class.id}/subjects",
        json={
            "subject_id": str(subject.id),
            "coefficient": 3,
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/classes/{academic_class.id}/subjects",
        json={
            "subject_id": str(subject.id),
            "coefficient": 3,
        },
    )

    assert second_response.status_code == 409


def test_assign_subject_with_option_http_sqlite_success():
    client, academic_class, subject, option = (
        create_test_environment()
    )

    response = client.post(
        f"/classes/{academic_class.id}/subjects",
        json={
            "subject_id": str(subject.id),
            "coefficient": 3,
            "academic_option_id": str(option.id),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["academic_class_id"] == str(
        academic_class.id
    )

    assert data["subject_id"] == str(
        subject.id
    )

    assert data["academic_option_id"] == str(
        option.id
    )

    assert data["coefficient"] == 3

