from sqlite3 import Connection


version = "046"


def upgrade(connection: Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS google_auth_nonces (
            nonce_hash TEXT PRIMARY KEY,
            expires_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_google_auth_nonces_expires_at "
        "ON google_auth_nonces (expires_at)"
    )
