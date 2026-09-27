from pathlib import Path
from uuid import uuid4

from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)

TEST_DATABASE_DIRECTORY = (
    Path(__file__).parent / "databases"
)


def create_record() -> StudentAcademicRecord:
    return StudentAcademicRecord(
        tenant_id=uuid4(),
        student_id=uuid4(),
        academic_period_id=uuid4(),
        subject_results=(
            SubjectResult(
                subject_id=uuid4(),
                average=15.0,
                coefficient=2.0,
            ),
            SubjectResult(
                subject_id=uuid4(),
                average=12.0,
                coefficient=3.0,
            ),
        ),
        general_average=13.2,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )


def create_repository() -> SQLiteStudentAcademicRecordRepository:
    TEST_DATABASE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    database_path = (
        TEST_DATABASE_DIRECTORY
        / f"edunova_test_{uuid4().hex}.db"
    )

    database = SQLiteDatabase(database_path)
    database.initialize()

    return SQLiteStudentAcademicRecordRepository(database)


def create_student(
    repository: SQLiteStudentAcademicRecordRepository,
    record: StudentAcademicRecord,
) -> None:
    database = repository._database

    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO students (
                id,
                tenant_id,
                first_name,
                last_name,
                email,
                phone,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(record.student_id),
                str(record.tenant_id),
                "Test",
                "Student",
                None,
                None,
                1,
            ),
        )


def test_sql_repository_can_save_and_reload_record():
    repository = create_repository()
    record = create_record()

    create_student(repository, record)

    repository.save(record)

    result = repository.find_by_student_and_period(
        record.student_id,
        record.academic_period_id,
        record.tenant_id,
    )

    assert result == record


def test_sql_repository_returns_none_for_unknown_student():
    repository = create_repository()

    result = repository.find_by_student(uuid4(), uuid4())

    assert result is None


def test_sql_repository_returns_none_for_unknown_period():
    repository = create_repository()
    record = create_record()

    create_student(repository, record)

    repository.save(record)

    result = repository.find_by_student_and_period(
        record.student_id,
        uuid4(),
        record.tenant_id,
    )

    assert result is None


def test_sql_repository_preserves_subject_results():
    repository = create_repository()
    record = create_record()

    create_student(repository, record)

    repository.save(record)

    result = repository.find_by_student_and_period(
        record.student_id,
        record.academic_period_id,
        record.tenant_id,
    )

    assert result is not None
    assert len(result.subject_results) == 2

    assert (
        result.subject_results[0].subject_id
        == record.subject_results[0].subject_id
    )

    assert (
        result.subject_results[0].average
        == record.subject_results[0].average
    )

    assert (
        result.subject_results[0].coefficient
        == record.subject_results[0].coefficient
    )

    assert (
        result.subject_results[1].subject_id
        == record.subject_results[1].subject_id
    )

    assert (
        result.subject_results[1].average
        == record.subject_results[1].average
    )

    assert (
        result.subject_results[1].coefficient
        == record.subject_results[1].coefficient
    )


def test_sql_repository_replaces_existing_record():
    repository = create_repository()
    record = create_record()

    create_student(repository, record)

    repository.save(record)

    updated = StudentAcademicRecord(
        tenant_id=record.tenant_id,
        student_id=record.student_id,
        academic_period_id=record.academic_period_id,
        subject_results=(
            SubjectResult(
                subject_id=uuid4(),
                average=18.0,
                coefficient=4.0,
            ),
        ),
        general_average=18.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )

    repository.save(updated)

    result = repository.find_by_student_and_period(
        record.student_id,
        record.academic_period_id,
        record.tenant_id,
    )

    assert result == updated

