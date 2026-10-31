from sqlite3 import Connection


version = "038"


def upgrade(connection: Connection) -> None:
    # Confirmed payments are financial ledger facts. Corrections must be
    # represented by counter-entries; changing or deleting the source payment
    # would destroy the audit trail and can invalidate receipts.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_payments_immutable_update
        BEFORE UPDATE ON billing_payments
        BEGIN
            SELECT RAISE(ABORT, 'billing payments are immutable; use a counter entry');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_payments_immutable_delete
        BEFORE DELETE ON billing_payments
        BEGIN
            SELECT RAISE(ABORT, 'billing payments are immutable; use a counter entry');
        END
    """)
