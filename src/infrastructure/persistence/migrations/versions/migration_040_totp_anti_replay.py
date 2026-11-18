from sqlite3 import Connection


version = "040"


def upgrade(connection: Connection) -> None:
    """Atomic TOTP anti-replay protection table.

    Tracks the last accepted TOTP time interval per user to prevent
    code reuse across server restarts and multiple processes.

    The ON CONFLICT ... WHERE clause ensures atomicity:
    - Only accepts interval if strictly greater than last accepted
    - Prevents replay even with concurrent requests
    """
    connection.execute("""
        CREATE TABLE IF NOT EXISTS totp_anti_replay (
            user_id TEXT PRIMARY KEY,
            last_accepted_interval INTEGER NOT NULL
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_totp_anti_replay_user_id
        ON totp_anti_replay (user_id)
    """)
