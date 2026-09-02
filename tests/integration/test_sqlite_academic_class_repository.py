from uuid import uuid4

from src.domain.entities.academic_class import AcademicClass
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_academic_class_repository import (
    SQLiteAcademicClassRepository,
)


def test_academic_class_can_be_saved_and_found_by_id():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteAcademicClassRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        name="6e Scientifique",
    )

    repository.save(academic_class)

    result = repository.find_by_id(academic_class.id)

    assert result == academic_class


def test_academic_class_returns_none_when_not_found():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteAcademicClassRepository(database)

    result = repository.find_by_id(uuid4())

    assert result is None
