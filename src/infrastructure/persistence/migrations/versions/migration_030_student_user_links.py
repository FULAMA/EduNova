from sqlite3 import Connection


version = "030"


def upgrade(connection: Connection) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS student_user_links (
            tenant_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (tenant_id, user_id),
            UNIQUE (tenant_id, student_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (tenant_id, student_id)
                REFERENCES students (tenant_id, id)
        )"""
    )

