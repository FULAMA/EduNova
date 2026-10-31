import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_033_fee_applicability,
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
    return connection


def _insert_fee_type(
    connection: sqlite3.Connection,
    *,
    fee_id: str = "fee-1",
    tenant_id: str = "tenant-1",
    applicability: str = "STUDENT",
    target_class_id: str | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO billing_fee_types
            (id, tenant_id, applicability, target_class_id)
        VALUES (?, ?, ?, ?)
        """,
        (fee_id, tenant_id, applicability, target_class_id),
    )


def test_migration_033_adds_columns_and_allows_valid_student_fee() -> None:
    connection = _connection()
    _insert_fee_type(connection)

    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(billing_fee_types)"
        ).fetchall()
    }
    assignment_columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(billing_fee_assignments)"
        ).fetchall()
    }

    assert "target_class_id" in columns
    assert "snapshot_class_id" in assignment_columns


@pytest.mark.parametrize(
    ("applicability", "target_class_id"),
    [("CLASS", None), ("STUDENT", "class-1")],
)
def test_migration_033_rejects_inconsistent_fee_target(
    applicability: str,
    target_class_id: str | None,
) -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="fee target class"):
        _insert_fee_type(
            connection,
            applicability=applicability,
            target_class_id=target_class_id,
        )


def test_migration_033_rejects_target_class_from_another_tenant() -> None:
    connection = _connection()
    connection.execute(
        "INSERT INTO academic_classes (id, tenant_id) VALUES ('class-1', 'tenant-2')"
    )

    with pytest.raises(sqlite3.IntegrityError, match="fee target class"):
        _insert_fee_type(
            connection,
            applicability="CLASS",
            target_class_id="class-1",
        )


def test_migration_033_requires_assignment_snapshot_to_match_class_fee() -> None:
    connection = _connection()
    connection.execute(
        "INSERT INTO academic_classes (id, tenant_id) VALUES ('class-1', 'tenant-1')"
    )
    connection.execute(
        "INSERT INTO academic_classes (id, tenant_id) VALUES ('class-2', 'tenant-1')"
    )
    _insert_fee_type(
        connection,
        applicability="CLASS",
        target_class_id="class-1",
    )

    with pytest.raises(
        sqlite3.IntegrityError,
        match="preserve its target class",
    ):
        connection.execute(
            """
            INSERT INTO billing_fee_assignments
                (id, tenant_id, fee_type_id, snapshot_class_id)
            VALUES ('assignment-1', 'tenant-1', 'fee-1', 'class-2')
            """
        )


def test_migration_033_rejects_cross_tenant_assignment_snapshot_class() -> None:
    connection = _connection()
    connection.execute(
        "INSERT INTO academic_classes (id, tenant_id) VALUES ('class-1', 'tenant-2')"
    )
    _insert_fee_type(connection)

    with pytest.raises(
        sqlite3.IntegrityError,
        match="snapshot class must belong to the same tenant",
    ):
        connection.execute(
            """
            INSERT INTO billing_fee_assignments
                (id, tenant_id, fee_type_id, snapshot_class_id)
            VALUES ('assignment-1', 'tenant-1', 'fee-1', 'class-1')
            """
        )


def test_migration_033_makes_assignment_snapshots_immutable() -> None:
    connection = _connection()
    _insert_fee_type(connection)
    connection.execute(
        """
        INSERT INTO billing_fee_assignments
            (id, tenant_id, fee_type_id, snapshot_name)
        VALUES ('assignment-1', 'tenant-1', 'fee-1', 'Frais scolaires')
        """
    )

    with pytest.raises(
        sqlite3.IntegrityError,
        match="fee assignment snapshots are immutable",
    ):
        connection.execute(
            """
            UPDATE billing_fee_assignments
            SET snapshot_name = 'Valeur modifiée'
            WHERE tenant_id = 'tenant-1' AND id = 'assignment-1'
            """
        )


def test_migration_033_is_safe_to_rerun() -> None:
    connection = _connection()
    migration_033_fee_applicability.upgrade(connection)
