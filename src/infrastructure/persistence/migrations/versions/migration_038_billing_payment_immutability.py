from sqlite3 import Connection


version = "038"


def upgrade(connection: Connection) -> None:
    """Keep confirmed payment records append-only; corrections use counter-entries."""
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_payments_no_update
        BEFORE UPDATE ON billing_payments
        BEGIN
            SELECT RAISE(ABORT, 'billing payments are immutable; use a counter-entry');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_payments_no_delete
        BEFORE DELETE ON billing_payments
        BEGIN
            SELECT RAISE(ABORT, 'billing payments are immutable; use a counter-entry');
        END
    """)
