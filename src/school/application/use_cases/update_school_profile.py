from uuid import UUID

from src.school.application.interfaces.school_profile_repository import SchoolProfileRepository
from src.school.domain.entities.school_profile import SchoolProfile


class UpdateSchoolProfile:
    def __init__(self, profiles: SchoolProfileRepository) -> None:
        self._profiles = profiles

    def execute(
        self, tenant_id: UUID, actor_user_id: UUID, legal_name: str, display_name: str,
        address: str | None = None, phone: str | None = None,
        email: str | None = None, website: str | None = None,
        logo_url: str | None = None,
    ) -> SchoolProfile:
        profile = SchoolProfile(
            tenant_id=tenant_id, legal_name=legal_name, display_name=display_name,
            address=address, phone=phone, email=email, website=website,
            logo_url=logo_url,
        )
        return self._profiles.save(profile, actor_user_id)
