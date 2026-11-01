from uuid import UUID

from src.school.application.interfaces.school_profile_repository import SchoolProfileRepository
from src.school.domain.entities.school_profile import SchoolProfile


class GetSchoolProfile:
    def __init__(self, profiles: SchoolProfileRepository) -> None:
        self._profiles = profiles

    def execute(self, tenant_id: UUID) -> SchoolProfile | None:
        return self._profiles.find_by_tenant(tenant_id)
