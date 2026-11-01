from typing import Protocol
from uuid import UUID

from src.school.domain.entities.school_profile import SchoolProfile


class SchoolProfileRepository(Protocol):
    def find_by_tenant(self, tenant_id: UUID) -> SchoolProfile | None: ...
    def save(self, profile: SchoolProfile) -> SchoolProfile: ...
