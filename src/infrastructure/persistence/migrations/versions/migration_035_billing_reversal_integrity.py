from sqlite3 import Connection


version = "035"


def upgrade(connection: Connection) -> None:
    # A counter-entry is valid only when the original payment has its receipt.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_counter_entry_requires_receipt
        BEFORE INSERT ON billing_counter_entries
        WHEN NOT EXISTS (
            SELECT 1 FROM billing_receipts
            WHERE tenant_id = NEW.tenant_id
              AND payment_id = NEW.original_payment_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'counter entry requires an issued receipt');
        END
    """)

    # A reversed receipt must point to the counter-entry for the same payment
    # and tenant. This also prevents dangling or cross-tenant references.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_receipt_reversal_link
        BEFORE UPDATE OF status, reversed_by_entry_id ON billing_receipts
        WHEN
            (NEW.status = 'ISSUED' AND NEW.reversed_by_entry_id IS NOT NULL)
            OR
            (NEW.status = 'REVERSED' AND (
                NEW.reversed_by_entry_id IS NULL
                OR NOT EXISTS (
                    SELECT 1 FROM billing_counter_entries
                    WHERE tenant_id = NEW.tenant_id
                      AND id = NEW.reversed_by_entry_id
                      AND original_payment_id = NEW.payment_id
                )
            ))
        BEGIN
            SELECT RAISE(ABORT, 'receipt reversal must reference its payment counter entry');
        END
    """)

    # Financial correction records are append-only audit evidence.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_counter_entries_immutable_update
        BEFORE UPDATE ON billing_counter_entries
        BEGIN
            SELECT RAISE(ABORT, 'counter entries are immutable');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_counter_entries_immutable_delete
        BEFORE DELETE ON billing_counter_entries
        BEGIN
            SELECT RAISE(ABORT, 'counter entries are immutable');
        END
    """)
