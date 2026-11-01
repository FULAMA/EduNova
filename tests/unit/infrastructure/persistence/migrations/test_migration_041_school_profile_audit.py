import sqlite3

import pytest

from src.infrastructure.persistence.migrations.versions.migration_041_school_profile_audit import upgrade


def test_school_profile_audit_is_immutable():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE tenants (id TEXT PRIMARY KEY)")
    connection.execute("INSERT INTO tenants (id) VALUES ('tenant-a')")
    upgrade(connection)
    connection.execute("""
        INSERT INTO school_profile_audit
            (id, tenant_id, actor_user_id, action, after_state)
        VALUES ('event-1', 'tenant-a', 'user-1', 'CREATE', '{}')
    """)
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        connection.execute(
            "UPDATE school_profile_audit SET after_state = '{\"tampered\": true}' WHERE id = 'event-1'"
        )
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        connection.execute("DELETE FROM school_profile_audit WHERE id = 'event-1'")


def test_school_profile_audit_rejects_unknown_tenant_when_foreign_keys_enabled():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("CREATE TABLE tenants (id TEXT PRIMARY KEY)")
    upgrade(connection)
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO school_profile_audit
                (id, tenant_id, actor_user_id, action, after_state)
            VALUES ('event-1', 'unknown', 'user-1', 'CREATE', '{}')
        """)
