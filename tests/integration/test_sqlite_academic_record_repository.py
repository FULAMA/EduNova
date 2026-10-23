import json
import sqlite3
from uuid import uuid4

import pytest

from src.academic.domain.entities.student_academic_record import (
    AcademicRecordStatus,
    StudentAcademicRecord,
)
from src.academic.domain.value_objects.subject_result import SubjectResult
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


def test_sqlite_repository_saves_and_retrieves_academic_record(
    tmp_path,
):
    database_path = tmp_path / "test_edunova.db"
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


def test_sqlite_repository_keeps_correction_actor_and_reason_in_history(tmp_path):
    database = SQLiteDatabase(tmp_path / "audit.db")
    database.initialize()
    seed_tenant(database)

    student_id = uuid4()
    seed_student(database, student_id)
    period_id = uuid4()
    actor_id = uuid4()
    repository = SQLiteStudentAcademicRecordRepository(database)
    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=12.0,
        failed_subjects=0,
        credits_obtained=0.0,
        total_credits=30.0,
        status=AcademicRecordStatus.VALIDATED,
        version=2,
    )

    repository.save(
        record,
        operation="CORRECTED",
        actor_id=actor_id,
        reason="Correction de test",
    )

    with database.connect() as connection:
        row = connection.execute(
            "SELECT snapshot_json FROM student_academic_record_history "
            "WHERE operation = 'CORRECTED'"
        ).fetchone()

    snapshot = json.loads(row["snapshot_json"])
    assert snapshot["actor_id"] == str(actor_id)
    assert snapshot["reason"] == "Correction de test"


def test_sqlite_correction_rolls_back_when_history_is_unavailable(tmp_path):
    database = SQLiteDatabase(tmp_path / "audit-failure.db")
    database.initialize()
    seed_tenant(database)

    student_id = uuid4()
    period_id = uuid4()
    seed_student(database, student_id)
    repository = SQLiteStudentAcademicRecordRepository(database)
    record = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=12.0,
        failed_subjects=0,
        credits_obtained=0.0,
        total_credits=30.0,
        status=AcademicRecordStatus.VALIDATED,
        version=2,
    )
    repository.save(record)

    with database.connect() as connection:
        connection.execute("DROP TABLE student_academic_record_history")

    corrected = StudentAcademicRecord(
        tenant_id=TEST_TENANT_ID,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=13.0,
        failed_subjects=0,
        credits_obtained=0.0,
        total_credits=30.0,
        status=AcademicRecordStatus.VALIDATED,
        version=3,
    )

    with pytest.raises(sqlite3.OperationalError):
        repository.save(
            corrected,
            expected_version=2,
            operation="CORRECTED",
            actor_id=uuid4(),
            reason="Correction de test",
        )

    with database.connect() as connection:
        row = connection.execute(
            "SELECT version, general_average FROM student_academic_records "
            "WHERE student_id = ? AND academic_period_id = ?",
            (str(student_id), str(period_id)),
        ).fetchone()

    assert row["version"] == 2
    assert row["general_average"] == 12.0
