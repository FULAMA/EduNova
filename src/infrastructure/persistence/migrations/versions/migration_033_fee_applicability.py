from sqlite3 import Connection


version = "033"


def upgrade(connection: Connection) -> None:
    fee_columns = {
        row[1] for row in connection.execute(
            "PRAGMA table_info(billing_fee_types)"
        ).fetchall()
    }
    if "target_class_id" not in fee_columns:
        connection.execute(
            "ALTER TABLE billing_fee_types ADD COLUMN target_class_id TEXT"
        )

    assignment_columns = {
        row[1] for row in connection.execute(
            "PRAGMA table_info(billing_fee_assignments)"
        ).fetchall()
    }
    if "snapshot_class_id" not in assignment_columns:
        connection.execute(
            "ALTER TABLE billing_fee_assignments ADD COLUMN snapshot_class_id TEXT"
        )

    # Existing CLASS records are deliberately not assigned a guessed class.
    # They remain visible but cannot be newly assigned until corrected explicitly.
    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_fee_type_class_target_insert
        BEFORE INSERT ON billing_fee_types
        WHEN
            (NEW.applicability = 'CLASS' AND NEW.target_class_id IS NULL)
            OR (NEW.applicability != 'CLASS' AND NEW.target_class_id IS NOT NULL)
            OR (
                NEW.target_class_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM academic_classes
                    WHERE tenant_id = NEW.tenant_id AND id = NEW.target_class_id
                )
            )
        BEGIN
            SELECT RAISE(ABORT, 'fee target class must match applicability and tenant');
        END
    """)

    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_fee_type_class_target_update
        BEFORE UPDATE OF tenant_id, applicability, target_class_id
        ON billing_fee_types
        WHEN
            (NEW.applicability = 'CLASS' AND NEW.target_class_id IS NULL)
            OR (NEW.applicability != 'CLASS' AND NEW.target_class_id IS NOT NULL)
            OR (
                NEW.target_class_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM academic_classes
                    WHERE tenant_id = NEW.tenant_id AND id = NEW.target_class_id
                )
            )
        BEGIN
            SELECT RAISE(ABORT, 'fee target class must match applicability and tenant');
        END
    """)

    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_fee_assignment_class_snapshot_insert
        BEFORE INSERT ON billing_fee_assignments
        WHEN
            (
                SELECT applicability FROM billing_fee_types
                WHERE tenant_id = NEW.tenant_id AND id = NEW.fee_type_id
            ) = 'CLASS'
            AND (
                NEW.snapshot_class_id IS NULL
                OR NEW.snapshot_class_id != (
                    SELECT target_class_id FROM billing_fee_types
                    WHERE tenant_id = NEW.tenant_id AND id = NEW.fee_type_id
                )
            )
        BEGIN
            SELECT RAISE(ABORT, 'class fee assignment must preserve its target class');
        END
    """)

    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_fee_assignment_class_snapshot_tenant
        BEFORE INSERT ON billing_fee_assignments
        WHEN NEW.snapshot_class_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM academic_classes
            WHERE tenant_id = NEW.tenant_id AND id = NEW.snapshot_class_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'snapshot class must belong to the same tenant');
        END
    """)


    connection.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_fee_assignment_snapshot_immutable
        BEFORE UPDATE OF snapshot_name, snapshot_description, snapshot_category,
                         snapshot_applicability, amount, currency, snapshot_class_id
        ON billing_fee_assignments
        WHEN
            OLD.snapshot_name IS NOT NEW.snapshot_name
            OR OLD.snapshot_description IS NOT NEW.snapshot_description
            OR OLD.snapshot_category IS NOT NEW.snapshot_category
            OR OLD.snapshot_applicability IS NOT NEW.snapshot_applicability
            OR OLD.amount IS NOT NEW.amount
            OR OLD.currency IS NOT NEW.currency
            OR OLD.snapshot_class_id IS NOT NEW.snapshot_class_id
        BEGIN
            SELECT RAISE(ABORT, 'fee assignment snapshots are immutable');
        END
    """)
