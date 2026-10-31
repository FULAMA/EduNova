from sqlite3 import Connection


version = "037"


def upgrade(connection: Connection) -> None:
    # A reversal must be a faithful, single counter-entry for a confirmed payment.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_billing_counter_entry_matches_payment
        BEFORE INSERT ON billing_counter_entries
        WHEN
            NOT EXISTS (
                SELECT 1
                FROM billing_payments p
                JOIN billing_receipts r
                  ON r.tenant_id = p.tenant_id AND r.payment_id = p.id
                WHERE p.tenant_id = NEW.tenant_id
                  AND p.id = NEW.original_payment_id
                  AND p.status = 'CONFIRMED'
                  AND r.status = 'ISSUED'
                  AND p.currency = NEW.currency
                  AND CAST(p.amount AS NUMERIC) = CAST(NEW.amount AS NUMERIC)
                  AND r.currency = NEW.currency
                  AND CAST(r.amount AS NUMERIC) = CAST(NEW.amount AS NUMERIC)
            )
            OR length(trim(NEW.reason)) = 0
            OR length(trim(NEW.recorded_by)) = 0
            OR length(trim(NEW.recorded_at)) = 0
        BEGIN
            SELECT RAISE(ABORT, 'counter entry must faithfully reverse a confirmed payment with an issued receipt');
        END
    """)
