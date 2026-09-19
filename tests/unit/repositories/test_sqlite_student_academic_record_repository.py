import sqlite3
import pytest
from uuid import uuid4

from src.domain.entities.student_academic_record import (
    StudentAcademicRecord,
)
from src.domain.value_objects.subject_result import SubjectResult
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)
from src.infrastructure.persistence.database import SQLiteDatabase


def create_test_database(tmp_path):
    database_path = tmp_path / "test.db"

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript("""
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            active INTEGER NOT NULL
        );

        CREATE UNIQUE INDEX uq_students_tenant_id
        ON students (tenant_id, id);

        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,

            PRIMARY KEY (student_id, academic_period_id),

            FOREIGN KEY (tenant_id, student_id)
            REFERENCES students (tenant_id, id)
        );

        CREATE UNIQUE INDEX
        uq_student_academic_records_tenant_student_period
        ON student_academic_records (
            tenant_id,
            student_id,
            academic_period_id
        );

        CREATE TABLE subject_results (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            average REAL NOT NULL,
            coefficient REAL NOT NULL,
            position INTEGER NOT NULL,

            FOREIGN KEY (
                tenant_id,
                student_id,
                academic_period_id
            )
            REFERENCES student_academic_records (
                tenant_id,
                student_id,
                academic_period_id
            )
        );
    """)

    connection.commit()
    connection.close()

    return SQLiteDatabase(str(database_path))


def make_record(tenant_id, student_id, period_id):
    return StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )


def insert_student(database, student_id, tenant_id):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO students (
                id,
                tenant_id,
                first_name,
                last_name,
                active
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(student_id),
                str(tenant_id),
                "Jean",
                "Test",
                1,
            ),
        )


def insert_record(database, record, tenant_id):
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO student_academic_records (
                student_id,
                academic_period_id,
                tenant_id,
                general_average,
                failed_subjects,
                credits_obtained,
                total_credits
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(record.student_id),
                str(record.academic_period_id),
                str(tenant_id),
                record.general_average,
                record.failed_subjects,
                record.credits_obtained,
                record.total_credits,
            ),
        )


def test_find_by_student_and_period_requires_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_a,
    )

    assert result is not None
    assert result.student_id == student_id
    assert result.tenant_id == tenant_a


def test_find_by_student_and_period_cannot_cross_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student_and_period(
        student_id,
        period_id,
        tenant_b,
    )

    assert result is None

def test_find_by_student_requires_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student(
        student_id,
        tenant_a,
    )

    assert result is not None
    assert result.student_id == student_id
    assert result.tenant_id == tenant_a


def test_find_by_student_cannot_cross_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(tenant_a, student_id, period_id)
    insert_record(database, record, tenant_a)

    result = repository.find_by_student(
        student_id,
        tenant_b,
    )

    assert result is None

def test_save_persists_tenant_id(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_id)

    record = make_record(
        tenant_id,
        student_id,
        period_id,
    )

    repository.save(record)

    with database.connect() as connection:
        row = connection.execute(
            """
            SELECT
                tenant_id,
                student_id,
                academic_period_id
            FROM student_academic_records
            WHERE student_id = ?
              AND academic_period_id = ?
              AND tenant_id = ?
            """,
            (
                str(student_id),
                str(period_id),
                str(tenant_id),
            ),
        ).fetchone()

    assert row is not None
    assert row["tenant_id"] == str(tenant_id)
    assert row["student_id"] == str(student_id)
    assert row["academic_period_id"] == str(period_id)


def test_save_cannot_assign_record_to_another_tenant_student(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_id = uuid4()
    period_id = uuid4()

    insert_student(database, student_id, tenant_a)

    record = make_record(
        tenant_b,
        student_id,
        period_id,
    )

    with pytest.raises(sqlite3.IntegrityError):
        repository.save(record)


def test_save_persists_subject_results_for_same_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_id = uuid4()
    student_id = uuid4()
    period_id = uuid4()
    subject_id = uuid4()

    insert_student(database, student_id, tenant_id)

    record = StudentAcademicRecord(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_period_id=period_id,
        subject_results=(
            SubjectResult(
                subject_id=subject_id,
                average=15.0,
                coefficient=2.0,
            ),
        ),
        general_average=15.0,
        failed_subjects=0,
        credits_obtained=30.0,
        total_credits=30.0,
    )

    repository.save(record)

    with database.connect() as connection:
        row = connection.execute(
            """
            SELECT
                student_id,
                academic_period_id,
                subject_id
            FROM subject_results
            WHERE student_id = ?
              AND academic_period_id = ?
              AND subject_id = ?
            """,
            (
                str(student_id),
                str(period_id),
                str(subject_id),
            ),
        ).fetchone()

    assert row is not None
    assert row["student_id"] == str(student_id)
    assert row["academic_period_id"] == str(period_id)
    assert row["subject_id"] == str(subject_id)


def test_find_by_student_and_period_does_not_read_subject_results_from_another_tenant(
    tmp_path,
):
    database = create_test_database(tmp_path)
    repository = SQLiteStudentAcademicRecordRepository(database)

    tenant_a = uuid4()
    tenant_b = uuid4()

    student_a = uuid4()
    student_b = uuid4()
    period_id = uuid4()

    subject_a = uuid4()
    subject_b = uuid4()

    insert_student(database, student_a, tenant_a)
    insert_student(database, student_b, tenant_b)

    insert_record(
        database,
        make_record(
            tenant_b,
            student_b,
            period_id,
        ),
        tenant_b,
    )

    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO student_academic_records (
                student_id,
                academic_period_id,
                tenant_id,
                general_average,
                failed_subjects,
                credits_obtained,
                total_credits
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_a),
                str(period_id),
                str(tenant_a),
                15.0,
                0,
                30.0,
                30.0,
            ),
        )

        connection.execute(
            """
            INSERT INTO subject_results (
                student_id,
                academic_period_id,
                tenant_id,
                subject_id,
                average,
                coefficient,
                position
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_a),
                str(period_id),
                str(tenant_a),
                str(subject_a),
                15.0,
                2.0,
                0,
            ),
        )

        connection.execute(
            """
            INSERT INTO subject_results (
                student_id,
                academic_period_id,
                tenant_id,
                subject_id,
                average,
                coefficient,
                position
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(student_b),
                str(period_id),
                str(tenant_b),
                str(subject_b),
                18.0,
                3.0,
                0,
            ),
        )

    result = repository.find_by_student_and_period(
        student_a,
        period_id,
        tenant_a,
    )

    assert result is not None
    assert len(result.subject_results) == 1
    assert result.subject_results[0].subject_id == subject_a








