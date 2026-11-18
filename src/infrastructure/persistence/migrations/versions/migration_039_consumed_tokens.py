from sqlite3 import Connection


version = "039"


def upgrade(connection: Connection) -> None:
    """Atomic consumed tokens store for single-use token anti-replay."""
    connection.execute("""
        CREATE TABLE IF NOT EXISTS consumed_tokens (
            jti TEXT PRIMARY KEY,
            consumed_at TEXT NOT NULL
        )
    """)
