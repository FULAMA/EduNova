from uuid import uuid4

from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_school_profile_repository import SQLiteSchoolProfileRepository
from src.school.domain.entities.school_profile import SchoolProfile


def test_repository_round_trips_profiles_per_tenant_and_records_audit(tmp_path):
    database = SQLiteDatabase(tmp_path / "profiles.db")
    with database.connect() as connection:
        connection.execute("CREATE TABLE tenants (id TEXT PRIMARY KEY)")
        tenant_id = uuid4()
        other_tenant_id = uuid4()
        actor_id = uuid4()
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
        connection.execute("""
            CREATE TABLE school_profile_audit (
                id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, actor_user_id TEXT NOT NULL,
                action TEXT NOT NULL, before_state TEXT, after_state TEXT NOT NULL,
                occurred_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    repository = SQLiteSchoolProfileRepository(database)
    profile = SchoolProfile(tenant_id, "École Exemple ASBL", "École Exemple")
    repository.save(profile, actor_id)
    assert repository.find_by_tenant(tenant_id) == profile
    assert repository.find_by_tenant(other_tenant_id) is None
    changed = SchoolProfile(tenant_id, "École Exemple ASBL", "Exemple", phone="+243000000")
    repository.save(changed, actor_id)
    assert repository.find_by_tenant(tenant_id) == changed
    with database.connect() as connection:
        audit = connection.execute(
            "SELECT actor_user_id, action, before_state, after_state FROM school_profile_audit ORDER BY rowid"
        ).fetchall()
    assert len(audit) == 2
    assert audit[0]["actor_user_id"] == str(actor_id)
    assert audit[0]["action"] == "CREATE"
    assert audit[0]["before_state"] is None
    assert audit[1]["action"] == "UPDATE"
    assert '"display_name": "École Exemple"' in audit[1]["before_state"]
    assert '"display_name": "Exemple"' in audit[1]["after_state"]
