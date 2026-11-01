import json
from uuid import UUID, uuid4

from src.infrastructure.persistence.database import SQLiteDatabase
from src.school.domain.entities.school_profile import SchoolProfile


class SQLiteSchoolProfileRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    @staticmethod
    def _to_entity(row) -> SchoolProfile:
        return SchoolProfile(
            tenant_id=UUID(row["tenant_id"]), legal_name=row["legal_name"],
            display_name=row["display_name"], address=row["address"],
            phone=row["phone"], email=row["email"], website=row["website"],
            logo_url=row["logo_url"],
        )

    @staticmethod
    def _snapshot(profile: SchoolProfile | None) -> str | None:
        if profile is None:
            return None
        return json.dumps({
            "legal_name": profile.legal_name,
            "display_name": profile.display_name,
            "address": profile.address,
            "phone": profile.phone,
            "email": profile.email,
            "website": profile.website,
            "logo_url": profile.logo_url,
        }, ensure_ascii=False, sort_keys=True)

    def find_by_tenant(self, tenant_id: UUID) -> SchoolProfile | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """SELECT tenant_id, legal_name, display_name, address, phone,
                          email, website, logo_url
                   FROM school_profiles WHERE tenant_id = ?""",
                (str(tenant_id),),
            ).fetchone()
        return self._to_entity(row) if row is not None else None

    def save(self, profile: SchoolProfile, actor_user_id: UUID) -> SchoolProfile:
        with self._database.connect() as connection:
            current = connection.execute(
                """SELECT tenant_id, legal_name, display_name, address, phone,
                          email, website, logo_url
                   FROM school_profiles WHERE tenant_id = ?""",
                (str(profile.tenant_id),),
            ).fetchone()
            previous = self._to_entity(current) if current is not None else None
            connection.execute(
                """INSERT INTO school_profiles
                   (tenant_id, legal_name, display_name, address, phone, email, website, logo_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(tenant_id) DO UPDATE SET
                     legal_name = excluded.legal_name,
                     display_name = excluded.display_name,
                     address = excluded.address,
                     phone = excluded.phone,
                     email = excluded.email,
                     website = excluded.website,
                     logo_url = excluded.logo_url""",
                (str(profile.tenant_id), profile.legal_name, profile.display_name,
                 profile.address, profile.phone, profile.email, profile.website,
                 profile.logo_url),
            )
            connection.execute(
                """INSERT INTO school_profile_audit
                   (id, tenant_id, actor_user_id, action, before_state, after_state)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (str(uuid4()), str(profile.tenant_id), str(actor_user_id),
                 "CREATE" if previous is None else "UPDATE",
                 self._snapshot(previous), self._snapshot(profile)),
            )
        return profile
