import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import migration_012


def create_database():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
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
        );

        CREATE TABLE subject_results (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            average REAL NOT NULL,
            coefficient REAL NOT NULL,
            position INTEGER NOT NULL
        );
    """)

    return connection


def insert_student(connection, tenant_id, student_id):
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
            student_id,
            tenant_id,
            "Jean",
            "Test",
            1,
        ),
    )


def insert_record(connection, tenant_id, student_id, period_id):
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
            student_id,
            period_id,
            tenant_id,
            15.0,
            0,
            30.0,
            30.0,
        ),
    )


def insert_subject_result(
    connection,
    student_id,
    period_id,
    subject_id,
):
    connection.execute(
        """
        INSERT INTO subject_results (
            student_id,
            academic_period_id,
            subject_id,
            average,
            coefficient,
            position
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            period_id,
            subject_id,
            15.0,
            2.0,
            0,
        ),
    )


def test_migration_adds_tenant_id_and_preserves_data():
    connection = create_database()

    tenant_id = "tenant-a"
    student_id = "student-a"
    period_id = "period-a"
    subject_id = "subject-a"

    insert_student(connection, tenant_id, student_id)
    insert_record(connection, tenant_id, student_id, period_id)
    insert_subject_result(
        connection,
        student_id,
        period_id,
        subject_id,
    )

    migration_012.upgrade(connection)

    columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(subject_results)"
        ).fetchall()
    }

    assert "tenant_id" in columns

    row = connection.execute(
        """
        SELECT
            tenant_id,
            student_id,
            academic_period_id,
            subject_id
        FROM subject_results
        """
    ).fetchone()

    assert row is not None
    assert row["tenant_id"] == tenant_id
    assert row["student_id"] == student_id
    assert row["academic_period_id"] == period_id
    assert row["subject_id"] == subject_id


def test_migration_prevents_cross_tenant_subject_result():
    connection = create_database()

    tenant_a = "tenant-a"
    tenant_b = "tenant-b"
    student_id = "student-a"
    period_id = "period-a"

    insert_student(connection, tenant_a, student_id)
    insert_record(connection, tenant_a, student_id, period_id)

    insert_subject_result(
        connection,
        student_id,
        period_id,
        "subject-a",
    )

    migration_012.upgrade(connection)

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO subject_results (
                tenant_id,
                student_id,
                academic_period_id,
                subject_id,
                average,
                coefficient,
                position
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tenant_b,
                student_id,
                period_id,
                "subject-b",
                18.0,
                3.0,
                1,
            ),
        )


def test_migration_rejects_orphan_subject_results():
    connection = create_database()

    connection.execute(
        """
        INSERT INTO subject_results (
            student_id,
            academic_period_id,
            subject_id,
            average,
            coefficient,
            position
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "student-inexistant",
            "period-inexistant",
            "subject-a",
            15.0,
            2.0,
            0,
        ),
    )

    with pytest.raises(ValueError):
        migration_012.upgrade(connection)
