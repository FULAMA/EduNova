import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_016_tenant_scoped_academic_record_key,
)


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE students (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'DRAFT',
            PRIMARY KEY (student_id, academic_period_id),
            FOREIGN KEY (tenant_id, student_id)
            REFERENCES students (tenant_id, id)
        )
        """
    )


def test_migration_016_uses_tenant_scoped_primary_key() -> None:
    connection = sqlite3.connect(":memory:")
    create_schema(connection)
    connection.execute(
        "INSERT INTO students (id, tenant_id) VALUES (?, ?)",
        ("student-1", "tenant-1"),
    )
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
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("student-1", "period-1", "tenant-1", 15.0, 0, 30.0, 30.0),
    )

    migration_016_tenant_scoped_academic_record_key.upgrade(connection)

    columns = connection.execute(
        "PRAGMA table_info(student_academic_records)"
    ).fetchall()
    primary_key = [
        column[1]
        for column in sorted(columns, key=lambda column: column[5])
        if column[5] > 0
    ]

    assert primary_key == [
        "tenant_id",
        "student_id",
        "academic_period_id",
    ]
    assert connection.execute(
        "SELECT COUNT(*) FROM student_academic_records"
    ).fetchone()[0] == 1

    record = connection.execute(
        """
        SELECT tenant_id, student_id, academic_period_id,
               general_average, failed_subjects, credits_obtained,
               total_credits, version, status
        FROM student_academic_records
        """
    ).fetchone()
    assert tuple(record) == (
        "tenant-1",
        "student-1",
        "period-1",
        15.0,
        0,
        30.0,
        30.0,
        1,
        "DRAFT",
    )

    connection.execute(
        "INSERT INTO students (id, tenant_id) VALUES (?, ?)",
        ("student-1", "tenant-2"),
    )
    connection.execute(
        """
        INSERT INTO student_academic_records (
            student_id, academic_period_id, tenant_id,
            general_average, failed_subjects, credits_obtained,
            total_credits, version, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("student-1", "period-1", "tenant-2", 12.0, 1, 24.0, 30.0, 2, "VALIDATED"),
    )
    assert connection.execute(
        "SELECT COUNT(*) FROM student_academic_records"
    ).fetchone()[0] == 2
    assert connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall() == []

    index_names = {
        row[1]
        for row in connection.execute(
            "PRAGMA index_list(student_academic_records)"
        ).fetchall()
    }
    assert "uq_student_academic_records_tenant_student_period" in index_names


def test_migration_016_is_idempotent() -> None:
    connection = sqlite3.connect(":memory:")
    create_schema(connection)

    migration_016_tenant_scoped_academic_record_key.upgrade(connection)
    migration_016_tenant_scoped_academic_record_key.upgrade(connection)

    columns = connection.execute(
        "PRAGMA table_info(student_academic_records)"
    ).fetchall()
    assert sum(column[5] > 0 for column in columns) == 3


def test_migration_016_cleans_temporary_table_when_copy_fails() -> None:
    connection = sqlite3.connect(":memory:")
    create_schema(connection)
    connection.execute(
        "ALTER TABLE student_academic_records RENAME TO "
        "student_academic_records_without_version"
    )
    connection.execute(
        """
        CREATE TABLE student_academic_records (
            student_id TEXT NOT NULL,
            academic_period_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            general_average REAL NOT NULL,
            failed_subjects INTEGER NOT NULL,
            credits_obtained REAL NOT NULL,
            total_credits REAL NOT NULL,
            PRIMARY KEY (student_id, academic_period_id)
        )
        """
    )

    try:
        migration_016_tenant_scoped_academic_record_key.upgrade(connection)
    except sqlite3.OperationalError:
        pass
    else:
        raise AssertionError("La copie invalide devait échouer")

    assert connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = 'student_academic_records_new'
        """
    ).fetchone() is None
    assert connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = 'student_academic_records'
        """
    ).fetchone() is not None


def test_migration_016_rolls_back_failure_after_source_table_drop() -> None:
    connection = sqlite3.connect(":memory:")
    create_schema(connection)
    connection.execute(
        "INSERT INTO students (id, tenant_id) VALUES (?, ?)",
        ("student-1", "tenant-1"),
    )
    connection.execute(
        """
        INSERT INTO student_academic_records (
            student_id, academic_period_id, tenant_id,
            general_average, failed_subjects, credits_obtained,
            total_credits
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("student-1", "period-1", "tenant-1", 15.0, 0, 30.0, 30.0),
    )
    def deny_compatibility_index(action, first_argument, *_):
        if (
            action == sqlite3.SQLITE_CREATE_INDEX
            and first_argument
            == "uq_student_academic_records_tenant_student_period"
        ):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    connection.set_authorizer(deny_compatibility_index)

    try:
        with pytest.raises(sqlite3.DatabaseError):
            migration_016_tenant_scoped_academic_record_key.upgrade(
                connection
            )
    finally:
        connection.set_authorizer(None)

    record = connection.execute(
        """
        SELECT student_id, academic_period_id, tenant_id, general_average
        FROM student_academic_records
        """
    ).fetchone()
    assert tuple(record) == ("student-1", "period-1", "tenant-1", 15.0)
    assert connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = 'student_academic_records_new'
        """
    ).fetchone() is None
