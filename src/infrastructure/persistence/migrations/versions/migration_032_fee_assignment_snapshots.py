from sqlite3 import Connection


version = "032"


def upgrade(connection: Connection) -> None:
    # Fail before changing the schema if historical assignments cannot be
    # associated with a fee type in the same tenant. The snapshot columns are
    # NOT NULL, so silently backfilling from missing rows would otherwise
    # leave invalid history or make the migration fail halfway through.
    invalid_assignments = connection.execute(
        """
        SELECT COUNT(*)
        FROM billing_fee_assignments AS assignment
        LEFT JOIN billing_fee_types AS fee_type
          ON fee_type.id = assignment.fee_type_id
         AND fee_type.tenant_id = assignment.tenant_id
        WHERE fee_type.id IS NULL
           OR fee_type.name IS NULL
           OR fee_type.description IS NULL
           OR fee_type.category IS NULL
           OR fee_type.applicability IS NULL
           OR fee_type.amount IS NULL
           OR fee_type.currency IS NULL
        """
    ).fetchone()[0]

    if invalid_assignments:
        raise RuntimeError(
            "Migration 032 aborted: "
            f"{invalid_assignments} billing fee assignment(s) have no "
            "complete fee type in the same tenant. Repair these records "
            "before retrying the migration."
        )

    connection.execute(
        "ALTER TABLE billing_fee_assignments "
        "ADD COLUMN snapshot_name TEXT NOT NULL DEFAULT ''"
    )
    connection.execute(
        "ALTER TABLE billing_fee_assignments "
        "ADD COLUMN snapshot_description TEXT NOT NULL DEFAULT ''"
    )
    connection.execute(
        "ALTER TABLE billing_fee_assignments "
        "ADD COLUMN snapshot_category TEXT NOT NULL DEFAULT ''"
    )
    connection.execute(
        "ALTER TABLE billing_fee_assignments "
        "ADD COLUMN snapshot_applicability TEXT NOT NULL DEFAULT 'STUDENT'"
    )
    connection.execute(
        "ALTER TABLE billing_fee_assignments "
        "ADD COLUMN amount TEXT NOT NULL DEFAULT '0'"
    )
    connection.execute(
        "ALTER TABLE billing_fee_assignments "
        "ADD COLUMN currency TEXT NOT NULL DEFAULT 'USD'"
    )

    connection.execute(
        """
        UPDATE billing_fee_assignments
        SET
            snapshot_name = (
                SELECT name FROM billing_fee_types
                WHERE billing_fee_types.tenant_id = billing_fee_assignments.tenant_id
                  AND billing_fee_types.id = billing_fee_assignments.fee_type_id
            ),
            snapshot_description = (
                SELECT description FROM billing_fee_types
                WHERE billing_fee_types.tenant_id = billing_fee_assignments.tenant_id
                  AND billing_fee_types.id = billing_fee_assignments.fee_type_id
            ),
            snapshot_category = (
                SELECT category FROM billing_fee_types
                WHERE billing_fee_types.tenant_id = billing_fee_assignments.tenant_id
                  AND billing_fee_types.id = billing_fee_assignments.fee_type_id
            ),
            snapshot_applicability = (
                SELECT applicability FROM billing_fee_types
                WHERE billing_fee_types.tenant_id = billing_fee_assignments.tenant_id
                  AND billing_fee_types.id = billing_fee_assignments.fee_type_id
            ),
            amount = (
                SELECT amount FROM billing_fee_types
                WHERE billing_fee_types.tenant_id = billing_fee_assignments.tenant_id
                  AND billing_fee_types.id = billing_fee_assignments.fee_type_id
            ),
            currency = (
                SELECT currency FROM billing_fee_types
                WHERE billing_fee_types.tenant_id = billing_fee_assignments.tenant_id
                  AND billing_fee_types.id = billing_fee_assignments.fee_type_id
            )
        """
    )
