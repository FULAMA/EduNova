from pathlib import Path
from uuid import uuid4

from src.domain.entities.student_academic_record import StudentAcademicRecord
from src.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)
from tests.support.tenant import TEST_TENANT_ID


def seed_student(database, student_id):
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
                str(student_id),
                str(TEST_TENANT_ID),
                "Test",
                "Student",
                None,
                None,
                1,
            ),
        )


def seed_tenant(database):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO tenants (
                id,
                name,
                slug,
                active
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(TEST_TENANT_ID),
                "Tenant Test",
                "tenant-test",
                1,
            ),
        )


def test_sqlite_repository_saves_and_retrieves_academic_record():
    database_path = Path("tests/integration/test_edunova.db")

    if database_path.exists():
        database_path.unlink()

    database = SQLiteDatabase(database_path)
    database.initialize()

    seed_tenant(database)

    student_id = uuid4()
    seed_student(database, student_id)

    repository = SQLiteStudentAcademicRecordRepository(database)

    academic_period_id = uuid4()
    subject_id = uuid4()

    subject_result = SubjectResult(
        subject_id=subject_id,
        average=16.5,
        coefficient=3,
    )

    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
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
        TEST_TENANT_ID,
    )

    assert retrieved is not None
    assert retrieved.tenant_id == TEST_TENANT_ID
    assert retrieved.student_id == student_id
    assert retrieved.academic_period_id == academic_period_id
    assert retrieved.general_average == 16.5
    assert retrieved.failed_subjects == 0
    assert retrieved.credits_obtained == 30
    assert retrieved.total_credits == 30

    assert len(retrieved.subject_results) == 1

    retrieved_subject_result = retrieved.subject_results[0]

    assert retrieved_subject_result.subject_id == subject_id
    assert retrieved_subject_result.average == 16.5
    assert retrieved_subject_result.coefficient == 3
