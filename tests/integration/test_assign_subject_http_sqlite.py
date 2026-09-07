from uuid import uuid4

from fastapi.testclient import TestClient

from tests.auth_helpers import authenticate_as

from src.domain.entities.academic_class import AcademicClass
from src.domain.entities.academic_option import AcademicOption
from src.domain.entities.class_option import ClassOption
from src.domain.entities.subject import Subject
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
        name="6e Informatique",
    )

    subject = Subject(
        id=uuid4(),
        name="Algorithmique",
        code="ALGO",
        coefficient=3,
    )

    option = AcademicOption(
        id=uuid4(),
        name="Informatique",
        code="INFO",
    )

    class_option = ClassOption(
        id=uuid4(),
        academic_class_id=academic_class.id,
        academic_option_id=option.id,
    )

    academic_class_repository.save(academic_class)
    subject_repository.save(subject)
    academic_option_repository.save(option)
    class_option_repository.save(class_option)

    app = create_app(container)

    authenticate_as(app)

    return (
        TestClient(app),
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
