from sqlite3 import Connection


version = "018"


def upgrade(connection: Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS external_identities (
            id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            subject TEXT NOT NULL,
            user_id TEXT NOT NULL,

            UNIQUE (provider, subject),
            UNIQUE (provider, user_id),

            FOREIGN KEY (user_id)
                REFERENCES users (id)
                ON DELETE CASCADE
        )
        """
    )
