from sqlite3 import Connection


version = "034"


def upgrade(connection: Connection) -> None:
    # A class snapshot is meaningful only for a CLASS-applicable fee.
    # Keep this invariant in the database, not only in application validation.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_fee_assignment_snapshot_class_applicability_insert
        BEFORE INSERT ON billing_fee_assignments
        WHEN
            (
                NEW.snapshot_applicability = 'CLASS'
                AND (
                    NEW.snapshot_class_id IS NULL
                    OR NEW.snapshot_class_id != (
                        SELECT target_class_id FROM billing_fee_types
                        WHERE tenant_id = NEW.tenant_id AND id = NEW.fee_type_id
                    )
                )
            )
            OR (
                NEW.snapshot_applicability != 'CLASS'
                AND NEW.snapshot_class_id IS NOT NULL
            )
        BEGIN
            SELECT RAISE(ABORT, 'snapshot class must match snapshot applicability');
        END
    """)

    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_fee_assignment_snapshot_class_applicability_update
        BEFORE UPDATE OF snapshot_applicability, snapshot_class_id
        ON billing_fee_assignments
        WHEN
            (
                NEW.snapshot_applicability = 'CLASS'
                AND (
                    NEW.snapshot_class_id IS NULL
                    OR NEW.snapshot_class_id != (
                        SELECT target_class_id FROM billing_fee_types
                        WHERE tenant_id = NEW.tenant_id AND id = NEW.fee_type_id
                    )
                )
            )
            OR (
                NEW.snapshot_applicability != 'CLASS'
                AND NEW.snapshot_class_id IS NOT NULL
            )
        BEGIN
            SELECT RAISE(ABORT, 'snapshot class must match snapshot applicability');
        END
    """)
