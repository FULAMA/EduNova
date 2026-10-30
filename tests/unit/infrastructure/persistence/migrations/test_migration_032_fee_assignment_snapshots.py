import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_032_fee_assignment_snapshots,
)


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE billing_fee_types (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            name TEXT,
            description TEXT,
            category TEXT,
            applicability TEXT,
            amount TEXT,
            currency TEXT,
            PRIMARY KEY (tenant_id, id)
        );

        CREATE TABLE billing_fee_assignments (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            fee_type_id TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id)
        );
        """
    )
    return connection


def test_migration_032_rejects_orphaned_fee_assignment_before_schema_change():
    connection = _connection()
    connection.execute(
        """
        INSERT INTO billing_fee_assignments (id, tenant_id, fee_type_id)
        VALUES ('assignment-1', 'tenant-1', 'missing-fee')
        """
    )

    with pytest.raises(RuntimeError, match="1 billing fee assignment"):
        migration_032_fee_assignment_snapshots.upgrade(connection)

    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(billing_fee_assignments)"
        ).fetchall()
    }
    assert "snapshot_name" not in columns


def test_migration_032_backfills_snapshot_from_same_tenant_fee_type():
    connection = _connection()
    connection.execute(
        """
        INSERT INTO billing_fee_types (
            id, tenant_id, name, description, category,
            applicability, amount, currency
        )
        VALUES (
            'fee-1', 'tenant-1', 'Frais scolaires', 'Année scolaire',
            'SCHOOL', 'STUDENT', '250.00', 'USD'
        )
        """
    )
    connection.execute(
        """
        INSERT INTO billing_fee_assignments (id, tenant_id, fee_type_id)
        VALUES ('assignment-1', 'tenant-1', 'fee-1')
        """
    )

    migration_032_fee_assignment_snapshots.upgrade(connection)

    snapshot = connection.execute(
        """
        SELECT snapshot_name, snapshot_description, snapshot_category,
               snapshot_applicability, amount, currency
        FROM billing_fee_assignments
        WHERE tenant_id = 'tenant-1' AND id = 'assignment-1'
        """
    ).fetchone()

    assert snapshot == (
        "Frais scolaires",
        "Année scolaire",
        "SCHOOL",
        "STUDENT",
        "250.00",
        "USD",
    )
