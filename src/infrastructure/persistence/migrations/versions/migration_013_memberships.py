from sqlite3 import Connection


version = "013"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS memberships (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            role TEXT NOT NULL,
            active INTEGER NOT NULL,

            UNIQUE (
                user_id,
                tenant_id
            ),

            FOREIGN KEY (user_id)
                REFERENCES users (id)
                ON DELETE CASCADE,
            FOREIGN KEY (tenant_id)
                REFERENCES tenants (id)
                ON DELETE CASCADE
        )
    """)
