from sqlite3 import Connection


version = "023"


def upgrade(connection: Connection) -> None:
    columns = connection.execute("PRAGMA table_info(attendance_records)").fetchall()
    if not any(column[1] == "recorded_by" for column in columns):
        connection.execute(
            "ALTER TABLE attendance_records ADD COLUMN recorded_by TEXT"
        )
