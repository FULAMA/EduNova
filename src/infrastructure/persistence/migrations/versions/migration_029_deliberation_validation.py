from sqlite3 import Connection


version = "029"


def upgrade(connection: Connection) -> None:
    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(academic_deliberations)")
    }
    if "validated_by" not in columns:
        connection.execute(
            "ALTER TABLE academic_deliberations ADD COLUMN validated_by TEXT"
        )
    if "validated_at" not in columns:
        connection.execute(
            "ALTER TABLE academic_deliberations ADD COLUMN validated_at TEXT"
        )
