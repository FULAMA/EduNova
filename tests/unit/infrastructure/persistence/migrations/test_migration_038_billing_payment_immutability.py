import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_024_billing,
    migration_025_billing_corrections,
    migration_035_billing_reversal_integrity,
    migration_036_billing_receipt_immutability,
    migration_038_billing_payment_immutability,
)


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript("""
        CREATE TABLE students (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id)
        );
    """)
    for migration in (
        migration_024_billing,
        migration_025_billing_corrections,
        migration_035_billing_reversal_integrity,
        migration_036_billing_receipt_immutability,
        migration_038_billing_payment_immutability,
    ):
        migration.upgrade(connection)
    connection.execute(
        "INSERT INTO students (id, tenant_id) VALUES ('student-1', 'tenant-1')"
    )
    connection.execute("""
        INSERT INTO billing_charges
        (id, tenant_id, student_id, description, amount, currency, status)
        VALUES ('charge-1', 'tenant-1', 'student-1', 'Tuition', '100', 'USD', 'OPEN')
    """)
    connection.execute("""
        INSERT INTO billing_payments
        (id, tenant_id, charge_id, student_id, amount, currency, idempotency_key,
         status, recorded_by, recorded_at, receipt_number)
        VALUES ('payment-1', 'tenant-1', 'charge-1', 'student-1', '25', 'USD',
                'key-1', 'CONFIRMED', 'actor-1', 'now', 'REC-1')
    """)
    connection.execute("""
        INSERT INTO billing_receipts
        (number, tenant_id, payment_id, amount, currency, issued_at)
        VALUES ('REC-1', 'tenant-1', 'payment-1', '25', 'USD', 'now')
    """)
    return connection


def test_payment_financial_fields_and_status_are_immutable() -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="payments are immutable"):
        connection.execute(
            "UPDATE billing_payments SET amount = '1' WHERE tenant_id = 'tenant-1' AND id = 'payment-1'"
        )
    with pytest.raises(sqlite3.IntegrityError, match="payments are immutable"):
        connection.execute(
            "UPDATE billing_payments SET status = 'CANCELLED' WHERE tenant_id = 'tenant-1' AND id = 'payment-1'"
        )


def test_payment_cannot_be_deleted() -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="payments are immutable"):
        connection.execute(
            "DELETE FROM billing_payments WHERE tenant_id = 'tenant-1' AND id = 'payment-1'"
        )


def test_payment_immutability_migration_is_rerunnable() -> None:
    connection = _connection()
    migration_038_billing_payment_immutability.upgrade(connection)
    assert connection.execute(
        "SELECT amount, currency, status FROM billing_payments WHERE id = 'payment-1'"
    ).fetchone() == ('25', 'USD', 'CONFIRMED')
