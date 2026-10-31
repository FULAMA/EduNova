from sqlite3 import Connection


version = "037"


def upgrade(connection: Connection) -> None:
    # A reversal must exactly offset a confirmed payment. Enforce this at the
    # persistence boundary, not only in BillingService, so direct SQL writes
    # cannot corrupt the ledger.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_counter_entry_matches_payment
        BEFORE INSERT ON billing_counter_entries
        WHEN NOT EXISTS (
            SELECT 1 FROM billing_payments p
            WHERE p.tenant_id = NEW.tenant_id
              AND p.id = NEW.original_payment_id
              AND p.status = 'CONFIRMED'
              AND p.amount = NEW.amount
              AND p.currency = NEW.currency
        )
        BEGIN
            SELECT RAISE(ABORT, 'counter entry must match a confirmed payment');
        END
    """)
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_counter_entry_reason_required
        BEFORE INSERT ON billing_counter_entries
        WHEN NEW.reason IS NULL OR LENGTH(TRIM(NEW.reason)) = 0
             OR NEW.recorded_by IS NULL OR LENGTH(TRIM(NEW.recorded_by)) = 0
             OR NEW.recorded_at IS NULL OR LENGTH(TRIM(NEW.recorded_at)) = 0
        BEGIN
            SELECT RAISE(ABORT, 'counter entry audit fields are required');
        END
    """)
