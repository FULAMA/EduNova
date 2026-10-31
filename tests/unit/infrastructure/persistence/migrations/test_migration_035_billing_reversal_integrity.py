import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_024_billing,
    migration_025_billing_corrections,
    migration_035_billing_reversal_integrity,
)


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE students (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id)
        );
        """
    )
    migration_024_billing.upgrade(connection)
    migration_025_billing_corrections.upgrade(connection)
    migration_035_billing_reversal_integrity.upgrade(connection)
    return connection


def _seed_payment(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO students (id, tenant_id) VALUES ('student-1', 'tenant-1')"
    )
    connection.execute(
        """INSERT INTO billing_charges
           (id, tenant_id, student_id, description, amount, currency, status)
           VALUES ('charge-1', 'tenant-1', 'student-1', 'Tuition', '100', 'USD', 'OPEN')"""
    )
    connection.execute(
        """INSERT INTO billing_payments
           (id, tenant_id, charge_id, student_id, amount, currency, idempotency_key,
            status, recorded_by, recorded_at, receipt_number)
           VALUES ('payment-1', 'tenant-1', 'charge-1', 'student-1', '25', 'USD',
                   'key-1', 'CONFIRMED', 'actor-1', '2026-10-31T06:00:00+00:00', 'REC-1')"""
    )
    connection.execute(
        """INSERT INTO billing_receipts
           (number, tenant_id, payment_id, amount, currency, issued_at)
           VALUES ('REC-1', 'tenant-1', 'payment-1', '25', 'USD',
                   '2026-10-31T06:00:00+00:00')"""
    )


def _insert_counter_entry(connection: sqlite3.Connection, entry_id: str = "entry-1") -> None:
    connection.execute(
        """INSERT INTO billing_counter_entries
           (id, tenant_id, original_payment_id, amount, currency, reason, recorded_by, recorded_at)
           VALUES (?, 'tenant-1', 'payment-1', '25', 'USD', 'Correction', 'actor-1',
                   '2026-10-31T06:01:00+00:00')""",
        (entry_id,),
    )


def test_counter_entry_requires_original_receipt() -> None:
    connection = _connection()
    connection.execute(
        "INSERT INTO students (id, tenant_id) VALUES ('student-1', 'tenant-1')"
    )
    connection.execute(
        """INSERT INTO billing_charges
           (id, tenant_id, student_id, description, amount, currency, status)
           VALUES ('charge-1', 'tenant-1', 'student-1', 'Tuition', '100', 'USD', 'OPEN')"""
    )
    connection.execute(
        """INSERT INTO billing_payments
           (id, tenant_id, charge_id, student_id, amount, currency, idempotency_key,
            status, recorded_by, recorded_at, receipt_number)
           VALUES ('payment-1', 'tenant-1', 'charge-1', 'student-1', '25', 'USD',
                   'key-1', 'CONFIRMED', 'actor-1', 'now', 'REC-1')"""
    )
    with pytest.raises(sqlite3.IntegrityError, match="requires an issued receipt"):
        _insert_counter_entry(connection)


def test_reversed_receipt_must_reference_matching_counter_entry() -> None:
    connection = _connection()
    _seed_payment(connection)
    with pytest.raises(sqlite3.IntegrityError, match="must reference its payment counter entry"):
        connection.execute(
            "UPDATE billing_receipts SET status = 'REVERSED', reversed_by_entry_id = 'missing' "
            "WHERE tenant_id = 'tenant-1' AND payment_id = 'payment-1'"
        )


def test_reversed_receipt_accepts_matching_counter_entry() -> None:
    connection = _connection()
    _seed_payment(connection)
    _insert_counter_entry(connection)
    connection.execute(
        "UPDATE billing_receipts SET status = 'REVERSED', reversed_by_entry_id = 'entry-1' "
        "WHERE tenant_id = 'tenant-1' AND payment_id = 'payment-1'"
    )
    row = connection.execute(
        "SELECT status, reversed_by_entry_id FROM billing_receipts WHERE number = 'REC-1'"
    ).fetchone()
    assert row == ("REVERSED", "entry-1")


def test_counter_entries_are_append_only() -> None:
    connection = _connection()
    _seed_payment(connection)
    _insert_counter_entry(connection)
    with pytest.raises(sqlite3.IntegrityError, match="counter entries are immutable"):
        connection.execute(
            "UPDATE billing_counter_entries SET reason = 'Altered' WHERE id = 'entry-1'"
        )
    with pytest.raises(sqlite3.IntegrityError, match="counter entries are immutable"):
        connection.execute("DELETE FROM billing_counter_entries WHERE id = 'entry-1'")


def test_migration_035_is_safe_to_rerun() -> None:
    connection = _connection()
    migration_035_billing_reversal_integrity.upgrade(connection)
