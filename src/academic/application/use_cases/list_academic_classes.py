from uuid import UUID

from src.academic.application.interfaces.academic_class_repository import (
    AcademicClassRepository,
)
from src.academic.domain.entities.academic_class import AcademicClass


class ListAcademicClasses:
    def __init__(self, repository: AcademicClassRepository):
        self._repository = repository

    def execute(self, tenant_id: UUID) -> tuple[AcademicClass, ...]:
        return self._repository.list_by_tenant(tenant_id)
