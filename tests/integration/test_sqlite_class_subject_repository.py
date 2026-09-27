from tests.support.tenant import TEST_TENANT_ID
from uuid import uuid4

from src.academic.domain.entities.academic_class import AcademicClass
from src.academic.domain.entities.class_subject import ClassSubject
from src.academic.domain.entities.subject import Subject
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_academic_class_repository import (
    SQLiteAcademicClassRepository,
)
from src.infrastructure.repositories.sqlite_class_subject_repository import (
    SQLiteClassSubjectRepository,
)
from src.infrastructure.repositories.sqlite_subject_repository import (
    SQLiteSubjectRepository,
)


def test_class_subject_can_be_saved_and_found_by_id():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    class_repository = SQLiteAcademicClassRepository(database)
    subject_repository = SQLiteSubjectRepository(database)
    repository = SQLiteClassSubjectRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        name="6e Scientifique",
        tenant_id=TEST_TENANT_ID,
    )

    subject = Subject(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
        coefficient=3,
        tenant_id=TEST_TENANT_ID,
    )

    class_repository.save(academic_class)
    subject_repository.save(subject)

    class_subject = ClassSubject(
        id=uuid4(),
        academic_class_id=academic_class.id,
        subject_id=subject.id,
        coefficient=4,
        tenant_id=TEST_TENANT_ID,
    )

    repository.save(class_subject)

    result = repository.find_by_id(
        class_subject.id,
        TEST_TENANT_ID,
    )

    assert result == class_subject


def test_class_subject_returns_none_when_not_found():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    repository = SQLiteClassSubjectRepository(database)

    result = repository.find_by_id(
        uuid4(),
        TEST_TENANT_ID,
    )

    assert result is None


def test_class_subjects_can_be_found_by_class():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    class_repository = SQLiteAcademicClassRepository(database)
    subject_repository = SQLiteSubjectRepository(database)
    repository = SQLiteClassSubjectRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        name="6e Scientifique",
        tenant_id=TEST_TENANT_ID,
    )

    subject_one = Subject(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
        coefficient=3,
        tenant_id=TEST_TENANT_ID,
    )

    subject_two = Subject(
        id=uuid4(),
        name="Physique",
        code="PHY",
        coefficient=2,
        tenant_id=TEST_TENANT_ID,
    )

    class_repository.save(academic_class)
    subject_repository.save(subject_one)
    subject_repository.save(subject_two)

    class_subject_one = ClassSubject(
        id=uuid4(),
        academic_class_id=academic_class.id,
        subject_id=subject_one.id,
        coefficient=4,
        tenant_id=TEST_TENANT_ID,
    )

    class_subject_two = ClassSubject(
        id=uuid4(),
        academic_class_id=academic_class.id,
        subject_id=subject_two.id,
        coefficient=3,
        tenant_id=TEST_TENANT_ID,
    )

    repository.save(class_subject_one)
    repository.save(class_subject_two)

    result = repository.find_by_class(
        academic_class.id,
        TEST_TENANT_ID,
    )

    assert result == [
        class_subject_one,
        class_subject_two,
    ]


def test_class_subjects_can_be_found_by_class_and_option():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    class_repository = SQLiteAcademicClassRepository(database)
    subject_repository = SQLiteSubjectRepository(database)
    repository = SQLiteClassSubjectRepository(database)

    academic_class = AcademicClass(
        id=uuid4(),
        name="6e Scientifique",
        tenant_id=TEST_TENANT_ID,
    )

    subject = Subject(
        id=uuid4(),
        name="Mathématiques",
        code="MATH",
        coefficient=3,
        tenant_id=TEST_TENANT_ID,
    )

    academic_option_id = uuid4()

    class_repository.save(academic_class)
    subject_repository.save(subject)

    database.connect().execute(
        """
        INSERT INTO academic_options (
            id,
            name,
            code,
            active,
            tenant_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(academic_option_id),
            "Mathématiques",
            "MATH",
            1,
            str(TEST_TENANT_ID),
        ),
    )

    class_subject = ClassSubject(
        id=uuid4(),
        academic_class_id=academic_class.id,
        subject_id=subject.id,
        coefficient=4,
        academic_option_id=academic_option_id,
        tenant_id=TEST_TENANT_ID,
    )

    repository.save(class_subject)

    result = repository.find_by_class_and_option(
        academic_class.id,
        academic_option_id,
        TEST_TENANT_ID,
    )

    assert result == [class_subject]
