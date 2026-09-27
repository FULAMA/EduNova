import sqlite3

from src.infrastructure.persistence.migrations.versions import (
    migration_015_academic_record_status,
)


def test_migration_015_adds_status_column_with_draft_default():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE UNIQUE INDEX uq_students_tenant_id
        ON students (tenant_id, id)
    """)

    connection.execute("""
        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,

            PRIMARY KEY (
                student_id,
                academic_period_id
            ),

            FOREIGN KEY (
                tenant_id,
                student_id
            )
            REFERENCES students (
                tenant_id,
                id
            )
        )
    """)

    connection.execute("""
        INSERT INTO students (id, tenant_id)
        VALUES ('student-1', 'tenant-1')
    """)

    connection.execute("""
        INSERT INTO student_academic_records (
            student_id,
            academic_period_id,
            tenant_id,
            general_average,
            failed_subjects,
            credits_obtained,
            total_credits,
            version
        )
        VALUES (
            'student-1',
            'period-1',
            'tenant-1',
            15.0,
            0,
            30.0,
            30.0,
            2
        )
    """)

    migration_015_academic_record_status.upgrade(connection)

    columns = connection.execute("""
        PRAGMA table_info(student_academic_records)
    """).fetchall()

    column_names = [column[1] for column in columns]

    assert "status" in column_names

    row = connection.execute("""
        SELECT
            student_id,
            academic_period_id,
            tenant_id,
            version,
            status
        FROM student_academic_records
    """).fetchone()

    assert row == (
        "student-1",
        "period-1",
        "tenant-1",
        2,
        "DRAFT",
    )


def test_migration_015_is_idempotent():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE students (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE UNIQUE INDEX uq_students_tenant_id
        ON students (tenant_id, id)
    """)

    connection.execute("""
        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,

            PRIMARY KEY (
                student_id,
                academic_period_id
            ),

            FOREIGN KEY (
                tenant_id,
                student_id
            )
            REFERENCES students (
                tenant_id,
                id
            )
        )
    """)

    migration_015_academic_record_status.upgrade(connection)
    migration_015_academic_record_status.upgrade(connection)

    columns = connection.execute("""
        PRAGMA table_info(student_academic_records)
    """).fetchall()

    column_names = [column[1] for column in columns]

    assert column_names.count("status") == 1
