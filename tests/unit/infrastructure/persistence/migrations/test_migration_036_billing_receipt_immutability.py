import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_024_billing,
    migration_025_billing_corrections,
    migration_035_billing_reversal_integrity,
    migration_036_billing_receipt_immutability,
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
    migration_024_billing.upgrade(connection)
    migration_025_billing_corrections.upgrade(connection)
    migration_035_billing_reversal_integrity.upgrade(connection)
    migration_036_billing_receipt_immutability.upgrade(connection)
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


def _reverse(connection: sqlite3.Connection) -> None:
    connection.execute("""
        INSERT INTO billing_counter_entries
        (id, tenant_id, original_payment_id, amount, currency, reason, recorded_by, recorded_at)
        VALUES ('entry-1', 'tenant-1', 'payment-1', '25', 'USD', 'Correction', 'actor-1', 'later')
    """)
    connection.execute("""
        UPDATE billing_receipts
        SET status = 'REVERSED', reversed_by_entry_id = 'entry-1'
        WHERE tenant_id = 'tenant-1' AND payment_id = 'payment-1'
    """)


def test_issued_receipt_can_be_reversed_once() -> None:
    connection = _connection()
    _reverse(connection)
    assert connection.execute(
        "SELECT status, reversed_by_entry_id FROM billing_receipts WHERE number = 'REC-1'"
    ).fetchone() == ("REVERSED", "entry-1")


def test_reversed_receipt_cannot_be_reissued_or_relinked() -> None:
    connection = _connection()
    _reverse(connection)
    with pytest.raises(sqlite3.IntegrityError, match="billing receipts are immutable"):
        connection.execute(
            "UPDATE billing_receipts SET status = 'ISSUED', reversed_by_entry_id = NULL "
            "WHERE number = 'REC-1'"
        )
    with pytest.raises(sqlite3.IntegrityError, match="billing receipts are immutable"):
        connection.execute(
            "UPDATE billing_receipts SET reversed_by_entry_id = 'other-entry' "
            "WHERE number = 'REC-1'"
        )


def test_receipt_financial_identity_cannot_be_modified() -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="billing receipts are immutable"):
        connection.execute(
            "UPDATE billing_receipts SET amount = '999' WHERE number = 'REC-1'"
        )


def test_receipt_cannot_be_deleted() -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="billing receipts are immutable"):
        connection.execute("DELETE FROM billing_receipts WHERE number = 'REC-1'")


def test_migration_036_is_safe_to_rerun() -> None:
    connection = _connection()
    migration_036_billing_receipt_immutability.upgrade(connection)
