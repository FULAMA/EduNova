from sqlite3 import Connection


version = "007"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE TABLE subjects_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            coefficient REAL NOT NULL,
            active INTEGER NOT NULL,
            UNIQUE (tenant_id, code)
        )
    """)

    connection.execute("""
        INSERT INTO subjects_new (
            id,
            tenant_id,
            name,
            code,
            coefficient,
            active
        )
        SELECT
            id,
            tenant_id,
            name,
            code,
            coefficient,
            active
        FROM subjects
    """)

    connection.execute("""
        DROP TABLE subjects
    """)

    connection.execute("""
        ALTER TABLE subjects_new
        RENAME TO subjects
    """)

    connection.execute("""
        CREATE TABLE academic_options_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            active INTEGER NOT NULL,
            UNIQUE (tenant_id, code)
        )
    """)

    connection.execute("""
        INSERT INTO academic_options_new (
            id,
            tenant_id,
            name,
            code,
            active
        )
        SELECT
            id,
            tenant_id,
            name,
            code,
            active
        FROM academic_options
    """)

    connection.execute("""
        DROP TABLE academic_options
    """)

    connection.execute("""
        ALTER TABLE academic_options_new
        RENAME TO academic_options
    """)
