import sqlite3
from uuid import uuid4

import pytest

from src.infrastructure.persistence.migrations.versions import (
    migration_018_external_identities,
)


def test_migration_018_creates_external_identity_constraints():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("CREATE TABLE users (id TEXT PRIMARY KEY)")

    migration_018_external_identities.upgrade(connection)
    user_id = str(uuid4())
    connection.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
    connection.execute(
        """
        INSERT INTO external_identities (id, provider, subject, user_id)
        VALUES (?, ?, ?, ?)
        """,
        (str(uuid4()), "google", "subject-1", user_id),
    )

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO external_identities (id, provider, subject, user_id)
            VALUES (?, ?, ?, ?)
            """,
            (str(uuid4()), "google", "subject-1", user_id),
        )
