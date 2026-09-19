from sqlite3 import Connection


version = "006"


def _has_tenant_id_column(connection: Connection) -> bool:
    columns = connection.execute("""
        PRAGMA table_info(class_subjects)
    """).fetchall()

    return any(column[1] == "tenant_id" for column in columns)


def _has_legacy_rows_without_tenant(connection: Connection) -> bool:
    if not _has_tenant_id_column(connection):
        row = connection.execute("""
            SELECT 1
            FROM class_subjects
            LIMIT 1
        """).fetchone()

        return row is not None

    row = connection.execute("""
        SELECT 1
        FROM class_subjects
        WHERE tenant_id IS NULL
        LIMIT 1
    """).fetchone()

    return row is not None


def upgrade(connection: Connection) -> None:
    if _has_legacy_rows_without_tenant(connection):
        raise RuntimeError(
            "Migration 006 impossible : des associations "
            "classe-matière existantes n'ont pas de tenant_id. "
            "Aucune donnée n'a été supprimée."
        )

    connection.execute("""
        CREATE TABLE class_subjects_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            academic_class_id TEXT NOT NULL,
            subject_id TEXT NOT NULL,
            coefficient REAL NOT NULL,
            academic_option_id TEXT,
            active INTEGER NOT NULL,
            UNIQUE (
                academic_class_id,
                subject_id,
                academic_option_id
            )
        )
    """)

    if _has_tenant_id_column(connection):
        connection.execute("""
            INSERT INTO class_subjects_new (
                id,
                tenant_id,
                academic_class_id,
                subject_id,
                coefficient,
                academic_option_id,
                active
            )
            SELECT
                id,
                tenant_id,
                academic_class_id,
                subject_id,
                coefficient,
                academic_option_id,
                active
            FROM class_subjects
        """)

    connection.execute("""
        DROP TABLE class_subjects
    """)

    connection.execute("""
        ALTER TABLE class_subjects_new
        RENAME TO class_subjects
    """)

    connection.execute("""
        CREATE UNIQUE INDEX uq_class_subject_common
        ON class_subjects (
            academic_class_id,
            subject_id
        )
        WHERE academic_option_id IS NULL
    """)
