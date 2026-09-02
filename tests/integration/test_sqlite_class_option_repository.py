from uuid import uuid4

from src.domain.entities.academic_class import AcademicClass
from src.domain.entities.academic_option import AcademicOption
from src.domain.entities.class_option import ClassOption
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_academic_class_repository import (
    SQLiteAcademicClassRepository,
)
from src.infrastructure.repositories.sqlite_academic_option_repository import (
    SQLiteAcademicOptionRepository,
)
from src.infrastructure.repositories.sqlite_class_option_repository import (
    SQLiteClassOptionRepository,
)


def test_class_option_can_be_saved_and_found_by_id():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    class_repository = SQLiteAcademicClassRepository(database)
    option_repository = SQLiteAcademicOptionRepository(database)
    repository = SQLiteClassOptionRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        name="6e Scientifique",
    )

    academic_option = AcademicOption(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
    )

    class_repository.save(academic_class)
    option_repository.save(academic_option)

    class_option = ClassOption(
        id=uuid4(),
        academic_class_id=academic_class.id,
        academic_option_id=academic_option.id,
    )

    repository.save(class_option)

    result = repository.find_by_id(class_option.id)

    assert result == class_option


def test_class_option_returns_none_when_not_found():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteClassOptionRepository(database)

    result = repository.find_by_id(uuid4())

    assert result is None


def test_class_option_can_be_found_by_class_and_option():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    class_repository = SQLiteAcademicClassRepository(database)
    option_repository = SQLiteAcademicOptionRepository(database)
    repository = SQLiteClassOptionRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        name="6e Scientifique",
    )

    academic_option = AcademicOption(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
    )

    class_repository.save(academic_class)
    option_repository.save(academic_option)

    class_option = ClassOption(
        id=uuid4(),
        academic_class_id=academic_class.id,
        academic_option_id=academic_option.id,
    )

    repository.save(class_option)

    result = repository.find_by_class_and_option(
        academic_class.id,
        academic_option.id,
    )

    assert result == class_option


def test_class_option_returns_none_for_unknown_class_and_option():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteClassOptionRepository(database)

    result = repository.find_by_class_and_option(
        uuid4(),
        uuid4(),
    )

    assert result is None


def test_class_option_pair_must_be_unique():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    class_repository = SQLiteAcademicClassRepository(database)
    option_repository = SQLiteAcademicOptionRepository(database)
    repository = SQLiteClassOptionRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        name="6e Scientifique",
    )

    academic_option = AcademicOption(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
    )

    class_repository.save(academic_class)
    option_repository.save(academic_option)

    first = ClassOption(
        id=uuid4(),
        academic_class_id=academic_class.id,
        academic_option_id=academic_option.id,
    )

    second = ClassOption(
        id=uuid4(),
        academic_class_id=academic_class.id,
        academic_option_id=academic_option.id,
    )

    repository.save(first)

    try:
        repository.save(second)
    except Exception as exc:
        assert "UNIQUE" in str(exc).upper()
    else:
        raise AssertionError(
            "Une classe ne doit pas avoir deux fois la même option."
        )