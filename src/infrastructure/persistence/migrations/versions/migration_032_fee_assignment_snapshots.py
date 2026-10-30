from sqlite3 import Connection


version = "032"


def upgrade(connection: Connection) -> None:
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
