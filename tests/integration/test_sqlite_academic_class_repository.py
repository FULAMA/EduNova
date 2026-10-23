from tests.support.tenant import TEST_TENANT_ID
from uuid import UUID, uuid4

from src.academic.domain.entities.academic_class import AcademicClass
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
        tenant_id=TEST_TENANT_ID,
        name="6e Scientifique",
    )

    repository.save(academic_class)

    result = repository.find_by_id(academic_class.id, TEST_TENANT_ID)

    assert result == academic_class


def test_academic_class_returns_none_when_not_found():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteAcademicClassRepository(database)

    result = repository.find_by_id(uuid4(), TEST_TENANT_ID)

    assert result is None


def test_academic_class_list_is_scoped_to_tenant_and_sorted():
    database = SQLiteDatabase(":memory:")
    database.initialize()
    repository = SQLiteAcademicClassRepository(database)
    other_tenant_id = UUID("00000000-0000-0000-0000-000000000002")

    repository.save(AcademicClass(uuid4(), TEST_TENANT_ID, "Terminale"))
    repository.save(AcademicClass(uuid4(), TEST_TENANT_ID, "Seconde"))
    repository.save(AcademicClass(uuid4(), other_tenant_id, "Autre tenant"))

    result = repository.list_by_tenant(TEST_TENANT_ID)

    assert [academic_class.name for academic_class in result] == [
        "Seconde",
        "Terminale",
    ]





def test_academic_class_cannot_be_found_from_another_tenant():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteAcademicClassRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        tenant_id=TEST_TENANT_ID,
        name="6e Scientifique",
    )

    repository.save(academic_class)

    another_tenant_id = UUID("00000000-0000-0000-0000-000000000002")

    result = repository.find_by_id(
        academic_class.id,
        another_tenant_id,
    )

    assert result is None

