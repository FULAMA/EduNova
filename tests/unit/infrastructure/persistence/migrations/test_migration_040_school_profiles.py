import sqlite3

from src.infrastructure.persistence.migrations.versions.migration_040_school_profiles import upgrade


def test_school_profile_migration_creates_one_profile_per_tenant():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE tenants (id TEXT PRIMARY KEY)")
    connection.execute("INSERT INTO tenants (id) VALUES ('tenant-a')")
    upgrade(connection)
    connection.execute("""
        INSERT INTO school_profiles (tenant_id, legal_name, display_name)
        VALUES ('tenant-a', 'École Exemple ASBL', 'École Exemple')
    """)
    try:
        connection.execute("""
            INSERT INTO school_profiles (tenant_id, legal_name, display_name)
            VALUES ('tenant-a', 'Autre nom', 'Autre')
        """)
        assert False, "Une seule fiche doit exister par tenant."
    except sqlite3.IntegrityError:
        pass


def test_school_profile_migration_rejects_unknown_tenant_when_fk_enabled():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("CREATE TABLE tenants (id TEXT PRIMARY KEY)")
    upgrade(connection)
    try:
        connection.execute("""
            INSERT INTO school_profiles (tenant_id, legal_name, display_name)
            VALUES ('missing', 'École', 'École')
        """)
        assert False, "Le tenant doit exister."
    except sqlite3.IntegrityError:
        pass
