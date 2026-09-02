import sqlite3
from uuid import uuid4

import pytest

from src.domain.entities.academic_class import AcademicClass
from src.domain.entities.class_subject import ClassSubject
from src.domain.entities.subject import Subject
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


def create_database():
    database = SQLiteDatabase(":memory:")
    database.initialize()
    return database


def test_sqlite_rejects_duplicate_common_subject_for_same_class():
    database = create_database()

    class_repository = SQLiteAcademicClassRepository(database)
    subject_repository = SQLiteSubjectRepository(database)
    class_subject_repository = SQLiteClassSubjectRepository(database)

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

    class_repository.save(academic_class)
    subject_repository.save(subject)

    first = ClassSubject(
        id=uuid4(),
        academic_class_id=academic_class.id,
        subject_id=subject.id,
        coefficient=3,
        academic_option_id=None,
    )

    second = ClassSubject(
        id=uuid4(),
        academic_class_id=academic_class.id,
        subject_id=subject.id,
        coefficient=3,
        academic_option_id=None,
    )

    class_subject_repository.save(first)

    with pytest.raises(sqlite3.IntegrityError):
        class_subject_repository.save(second)
