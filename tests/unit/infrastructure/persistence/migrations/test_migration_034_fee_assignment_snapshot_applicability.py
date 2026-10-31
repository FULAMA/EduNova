import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_033_fee_applicability,
    migration_034_fee_assignment_snapshot_applicability,
)


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE academic_classes (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id)
        );
        CREATE TABLE billing_fee_types (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            applicability TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id)
        );
        CREATE TABLE billing_fee_assignments (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            fee_type_id TEXT NOT NULL,
            snapshot_name TEXT NOT NULL DEFAULT '',
            snapshot_description TEXT NOT NULL DEFAULT '',
            snapshot_category TEXT NOT NULL DEFAULT '',
            snapshot_applicability TEXT NOT NULL DEFAULT 'STUDENT',
            amount TEXT NOT NULL DEFAULT '0',
            currency TEXT NOT NULL DEFAULT 'USD',
            PRIMARY KEY (tenant_id, id)
        );
        """
    )
    migration_033_fee_applicability.upgrade(connection)
    migration_034_fee_assignment_snapshot_applicability.upgrade(connection)
    return connection


def _insert_fee(connection: sqlite3.Connection, applicability: str, target: str | None = None) -> None:
    connection.execute(
        "INSERT INTO billing_fee_types (id, tenant_id, applicability, target_class_id) VALUES ('fee-1', 'tenant-1', ?, ?)",
        (applicability, target),
    )


def test_rejects_class_snapshot_for_student_fee() -> None:
    connection = _connection()
    connection.execute("INSERT INTO academic_classes (id, tenant_id) VALUES ('class-1', 'tenant-1')")
    _insert_fee(connection, "STUDENT")

    with pytest.raises(sqlite3.IntegrityError, match="snapshot class must match"):
        connection.execute(
            """INSERT INTO billing_fee_assignments
               (id, tenant_id, fee_type_id, snapshot_applicability, snapshot_class_id)
               VALUES ('assignment-1', 'tenant-1', 'fee-1', 'STUDENT', 'class-1')"""
        )


def test_rejects_class_snapshot_for_establishment_fee() -> None:
    connection = _connection()
    connection.execute("INSERT INTO academic_classes (id, tenant_id) VALUES ('class-1', 'tenant-1')")
    _insert_fee(connection, "ESTABLISHMENT")

    with pytest.raises(sqlite3.IntegrityError, match="snapshot class must match"):
        connection.execute(
            """INSERT INTO billing_fee_assignments
               (id, tenant_id, fee_type_id, snapshot_applicability, snapshot_class_id)
               VALUES ('assignment-1', 'tenant-1', 'fee-1', 'ESTABLISHMENT', 'class-1')"""
        )


def test_allows_matching_class_snapshot() -> None:
    connection = _connection()
    connection.execute("INSERT INTO academic_classes (id, tenant_id) VALUES ('class-1', 'tenant-1')")
    _insert_fee(connection, "CLASS", "class-1")

    connection.execute(
        """INSERT INTO billing_fee_assignments
           (id, tenant_id, fee_type_id, snapshot_applicability, snapshot_class_id)
           VALUES ('assignment-1', 'tenant-1', 'fee-1', 'CLASS', 'class-1')"""
    )


def test_rejects_class_snapshot_added_by_update() -> None:
    connection = _connection()
    connection.execute("INSERT INTO academic_classes (id, tenant_id) VALUES ('class-1', 'tenant-1')")
    _insert_fee(connection, "STUDENT")
    connection.execute(
        """INSERT INTO billing_fee_assignments
           (id, tenant_id, fee_type_id, snapshot_applicability)
           VALUES ('assignment-1', 'tenant-1', 'fee-1', 'STUDENT')"""
    )

    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        connection.execute(
            """UPDATE billing_fee_assignments SET snapshot_class_id = 'class-1'
               WHERE tenant_id = 'tenant-1' AND id = 'assignment-1'"""
        )


def test_migration_034_is_safe_to_rerun() -> None:
    connection = _connection()
    migration_034_fee_assignment_snapshot_applicability.upgrade(connection)
