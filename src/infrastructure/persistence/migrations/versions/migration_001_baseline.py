from sqlite3 import Connection


version = "001"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS migration_baseline (
            id INTEGER PRIMARY KEY
        )
    """)
