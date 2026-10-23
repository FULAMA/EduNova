from sqlite3 import Connection


version = "017"


def upgrade(connection: Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS academic_periods (
            id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            PRIMARY KEY (tenant_id, id)
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_academic_periods_tenant_name
        ON academic_periods (tenant_id, name)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_subjects_tenant_name
        ON subjects (tenant_id, name)
        """
    )

