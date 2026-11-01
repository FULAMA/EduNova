from uuid import UUID

from src.infrastructure.persistence.database import SQLiteDatabase
from src.school.domain.entities.school_profile import SchoolProfile


class SQLiteSchoolProfileRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    @staticmethod
    def _to_entity(row) -> SchoolProfile:
        return SchoolProfile(
            tenant_id=UUID(row["tenant_id"]),
            legal_name=row["legal_name"],
            display_name=row["display_name"],
            address=row["address"],
            phone=row["phone"],
            email=row["email"],
            website=row["website"],
            logo_url=row["logo_url"],
        )

    def find_by_tenant(self, tenant_id: UUID) -> SchoolProfile | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """SELECT tenant_id, legal_name, display_name, address, phone,
                          email, website, logo_url
                   FROM school_profiles WHERE tenant_id = ?""",
                (str(tenant_id),),
            ).fetchone()
        return self._to_entity(row) if row is not None else None

    def save(self, profile: SchoolProfile) -> SchoolProfile:
        with self._database.connect() as connection:
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
                (
                    str(profile.tenant_id), profile.legal_name, profile.display_name,
                    profile.address, profile.phone, profile.email, profile.website,
                    profile.logo_url,
                ),
            )
        return profile
