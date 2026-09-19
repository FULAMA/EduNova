from tests.support.tenant import TEST_TENANT_ID
from uuid import uuid4

from src.domain.entities.subject import Subject
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_subject_repository import (
    SQLiteSubjectRepository,
)


def test_subject_can_be_saved_and_found_by_id():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteSubjectRepository(database)

    subject = Subject(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
        coefficient=3,
        tenant_id=TEST_TENANT_ID,
    )

    repository.save(subject)

    result = repository.find_by_id(subject.id, TEST_TENANT_ID)

    assert result == subject


def test_subject_returns_none_when_not_found():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteSubjectRepository(database)

    result = repository.find_by_id(uuid4(), TEST_TENANT_ID)

    assert result is None


def test_subject_code_must_be_unique():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteSubjectRepository(database)

    first = Subject(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
        coefficient=3,
        tenant_id=TEST_TENANT_ID,
    )

    second = Subject(
        id=uuid4(),
        name="Mathématique avancée",
        code="MATH",
        coefficient=4,
        tenant_id=TEST_TENANT_ID,
    )

    repository.save(first)

    try:
        repository.save(second)
    except Exception as exc:
        assert "UNIQUE" in str(exc).upper()
    else:
        raise AssertionError(
            "Deux matières ne doivent pas partager le même code."
        )

