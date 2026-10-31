import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_024_billing,
    migration_025_billing_corrections,
    migration_035_billing_reversal_integrity,
    migration_036_billing_receipt_immutability,
    migration_037_billing_counter_entry_integrity,
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
    migration_037_billing_counter_entry_integrity.upgrade(connection)
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


def _insert_entry(connection: sqlite3.Connection, *, amount='25', currency='USD',
                  reason='Correction', actor='actor-1', payment='payment-1') -> None:
    connection.execute("""
        INSERT INTO billing_counter_entries
        (id, tenant_id, original_payment_id, amount, currency, reason, recorded_by, recorded_at)
        VALUES ('entry-1', 'tenant-1', ?, ?, ?, ?, ?, 'later')
    """, (payment, amount, currency, reason, actor))


def test_counter_entry_must_match_confirmed_payment_amount_and_currency() -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="match a confirmed payment"):
        _insert_entry(connection, amount='24')
    with pytest.raises(sqlite3.IntegrityError, match="match a confirmed payment"):
        _insert_entry(connection, currency='CDF')


def test_counter_entry_cannot_reverse_non_confirmed_payment() -> None:
    connection = _connection()
    connection.execute(
        "UPDATE billing_payments SET status = 'CANCELLED' WHERE id = 'payment-1'"
    )
    with pytest.raises(sqlite3.IntegrityError, match="match a confirmed payment"):
        _insert_entry(connection)


def test_counter_entry_requires_non_blank_audit_fields() -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="audit fields"):
        _insert_entry(connection, reason='   ')
    with pytest.raises(sqlite3.IntegrityError, match="audit fields"):
        _insert_entry(connection, actor=' ')


def test_valid_counter_entry_is_accepted_and_migration_is_rerunnable() -> None:
    connection = _connection()
    _insert_entry(connection)
    migration_037_billing_counter_entry_integrity.upgrade(connection)
    assert connection.execute(
        "SELECT amount, currency FROM billing_counter_entries WHERE id = 'entry-1'"
    ).fetchone() == ('25', 'USD')
