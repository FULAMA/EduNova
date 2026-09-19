from sqlite3 import Connection


version = "008"


def upgrade(connection: Connection) -> None:
    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_academic_classes_tenant_id
        ON academic_classes (tenant_id, id)
    """)

    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_subjects_tenant_id
        ON subjects (tenant_id, id)
    """)

    connection.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_academic_options_tenant_id
        ON academic_options (tenant_id, id)
    """)
    connection.execute("PRAGMA foreign_keys = OFF")

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
            ),

            FOREIGN KEY (
                tenant_id,
                academic_class_id
            )
            REFERENCES academic_classes (
                tenant_id,
                id
            ),

            FOREIGN KEY (
                tenant_id,
                subject_id
            )
            REFERENCES subjects (
                tenant_id,
                id
            ),

            FOREIGN KEY (
                tenant_id,
                academic_option_id
            )
            REFERENCES academic_options (
                tenant_id,
                id
            )
        )
    """)

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

    connection.execute("""
        CREATE TABLE class_options_new (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            academic_class_id TEXT NOT NULL,
            academic_option_id TEXT NOT NULL,
            active INTEGER NOT NULL,

            UNIQUE (
                academic_class_id,
                academic_option_id
            ),

            FOREIGN KEY (
                tenant_id,
                academic_class_id
            )
            REFERENCES academic_classes (
                tenant_id,
                id
            ),

            FOREIGN KEY (
                tenant_id,
                academic_option_id
            )
            REFERENCES academic_options (
                tenant_id,
                id
            )
        )
    """)

    connection.execute("""
        INSERT INTO class_options_new (
            id,
            tenant_id,
            academic_class_id,
            academic_option_id,
            active
        )
        SELECT
            id,
            tenant_id,
            academic_class_id,
            academic_option_id,
            active
        FROM class_options
    """)

    connection.execute("""
        DROP TABLE class_options
    """)

    connection.execute("""
        ALTER TABLE class_options_new
        RENAME TO class_options
    """)

    connection.execute("PRAGMA foreign_keys = ON")

