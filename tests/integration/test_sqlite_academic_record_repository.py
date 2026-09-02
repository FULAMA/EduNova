from pathlib import Path
from uuid import uuid4

from src.domain.entities.student_academic_record import (
    StudentAcademicRecord,
)
from src.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)


def test_sqlite_repository_saves_and_retrieves_academic_record():
    database_path = Path("tests/integration/test_edunova.db")

    if database_path.exists():
        database_path.unlink()

    database = SQLiteDatabase(database_path)
    database.initialize()

    repository = SQLiteStudentAcademicRecordRepository(database)

    student_id = uuid4()
    academic_period_id = uuid4()
    subject_id = uuid4()

    subject_result = SubjectResult(
        subject_id=subject_id,
        average=16.5,
        coefficient=3,
    )

    record = StudentAcademicRecord(
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_results=(subject_result,),
        general_average=16.5,
        failed_subjects=0,
        credits_obtained=30,
        total_credits=30,
    )

    repository.save(record)

    retrieved = repository.find_by_student_and_period(
        student_id,
        academic_period_id,
    )

    assert retrieved is not None
    assert retrieved.student_id == student_id
    assert retrieved.academic_period_id == academic_period_id
    assert retrieved.general_average == 16.5
    assert retrieved.failed_subjects == 0
    assert retrieved.credits_obtained == 30
    assert retrieved.total_credits == 30

    assert len(retrieved.subject_results) == 1

    assert retrieved.subject_results[0].subject_id == subject_id
    assert retrieved.subject_results[0].average == 16.5
    assert retrieved.subject_results[0].coefficient == 3
