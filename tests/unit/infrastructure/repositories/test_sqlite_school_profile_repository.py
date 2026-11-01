from uuid import uuid4

from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_school_profile_repository import SQLiteSchoolProfileRepository
from src.school.domain.entities.school_profile import SchoolProfile


def test_repository_round_trips_profiles_per_tenant(tmp_path):
    database = SQLiteDatabase(tmp_path / "profiles.db")
    with database.connect() as connection:
        connection.execute("CREATE TABLE tenants (id TEXT PRIMARY KEY)")
        tenant_id = uuid4()
        other_tenant_id = uuid4()
        connection.execute("INSERT INTO tenants (id) VALUES (?)", (str(tenant_id),))
        connection.execute("INSERT INTO tenants (id) VALUES (?)", (str(other_tenant_id),))
        connection.execute("""
            CREATE TABLE school_profiles (
                tenant_id TEXT PRIMARY KEY, legal_name TEXT NOT NULL,
                display_name TEXT NOT NULL, address TEXT, phone TEXT,
                email TEXT, website TEXT, logo_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    repository = SQLiteSchoolProfileRepository(database)
    profile = SchoolProfile(tenant_id, "École Exemple ASBL", "École Exemple")
    repository.save(profile)
    assert repository.find_by_tenant(tenant_id) == profile
    assert repository.find_by_tenant(other_tenant_id) is None
    changed = SchoolProfile(tenant_id, "École Exemple ASBL", "Exemple", phone="+243000000")
    repository.save(changed)
    assert repository.find_by_tenant(tenant_id) == changed
