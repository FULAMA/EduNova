from sqlite3 import Connection


version = "036"


def upgrade(connection: Connection) -> None:
    # Receipts are immutable evidence. The sole permitted mutation is the
    # one-way ISSUED -> REVERSED transition with a valid counter-entry link.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_receipts_immutable_update
        BEFORE UPDATE ON billing_receipts
        WHEN
            NEW.number IS NOT OLD.number
            OR NEW.tenant_id IS NOT OLD.tenant_id
            OR NEW.payment_id IS NOT OLD.payment_id
            OR NEW.amount IS NOT OLD.amount
            OR NEW.currency IS NOT OLD.currency
            OR NEW.issued_at IS NOT OLD.issued_at
            OR (
                OLD.status = 'REVERSED'
                AND (
                    NEW.status IS NOT OLD.status
                    OR NEW.reversed_by_entry_id IS NOT OLD.reversed_by_entry_id
                )
            )
        BEGIN
            SELECT RAISE(ABORT, 'billing receipts are immutable');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_receipts_immutable_delete
        BEFORE DELETE ON billing_receipts
        BEGIN
            SELECT RAISE(ABORT, 'billing receipts are immutable');
        END
    """)
