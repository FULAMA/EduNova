import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_024_billing,
    migration_025_billing_corrections,
    migration_035_billing_reversal_integrity,
    migration_036_billing_receipt_immutability,
    migration_037_billing_counter_entry_consistency,
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
    migration_037_billing_counter_entry_consistency.upgrade(connection)
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


def _insert(connection: sqlite3.Connection, **overrides: str) -> None:
    values = {
        "id": "entry-1",
        "tenant_id": "tenant-1",
        "original_payment_id": "payment-1",
        "amount": "25",
        "currency": "USD",
        "reason": "Correction",
        "recorded_by": "actor-1",
        "recorded_at": "later",
    }
    values.update(overrides)
    connection.execute("""
        INSERT INTO billing_counter_entries
        (id, tenant_id, original_payment_id, amount, currency, reason, recorded_by, recorded_at)
        VALUES (:id, :tenant_id, :original_payment_id, :amount, :currency,
                :reason, :recorded_by, :recorded_at)
    """, values)


def test_accepts_counter_entry_matching_confirmed_payment_and_issued_receipt() -> None:
    connection = _connection()
    _insert(connection)
    assert connection.execute(
        "SELECT amount, currency FROM billing_counter_entries WHERE id = 'entry-1'"
    ).fetchone() == ("25", "USD")


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount": "24"},
        {"currency": "CDF"},
    ],
)
def test_rejects_counter_entry_with_amount_or_currency_mismatch(overrides: dict[str, str]) -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="faithfully reverse"):
        _insert(connection, **overrides)


def test_rejects_counter_entry_for_cancelled_payment() -> None:
    connection = _connection()
    connection.execute(
        "UPDATE billing_payments SET status = 'CANCELLED' WHERE tenant_id = 'tenant-1' AND id = 'payment-1'"
    )
    with pytest.raises(sqlite3.IntegrityError, match="faithfully reverse"):
        _insert(connection)


def test_rejects_counter_entry_when_receipt_is_not_issued() -> None:
    connection = _connection()
    # This represents a legacy/inconsistent state; the trigger must fail closed.
    connection.execute("DROP TRIGGER trg_billing_receipts_immutable_update")
    connection.execute("DROP TRIGGER trg_billing_receipt_reversal_link")
    connection.execute(
        "UPDATE billing_receipts SET status = 'REVERSED', reversed_by_entry_id = 'legacy-entry' "
        "WHERE tenant_id = 'tenant-1' AND payment_id = 'payment-1'"
    )
    with pytest.raises(sqlite3.IntegrityError, match="faithfully reverse"):
        _insert(connection)


@pytest.mark.parametrize("field,value", [("reason", "   "), ("recorded_by", " "), ("recorded_at", "")])
def test_rejects_blank_audit_metadata(field: str, value: str) -> None:
    connection = _connection()
    with pytest.raises(sqlite3.IntegrityError, match="faithfully reverse"):
        _insert(connection, **{field: value})


def test_migration_037_is_safe_to_rerun() -> None:
    connection = _connection()
    migration_037_billing_counter_entry_consistency.upgrade(connection)
