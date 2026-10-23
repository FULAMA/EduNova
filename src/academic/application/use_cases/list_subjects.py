from uuid import UUID

from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.subject import Subject


class ListSubjects:
    def __init__(self, repository: SubjectRepository):
        self._repository = repository

    def execute(self, tenant_id: UUID, search: str | None = None) -> list[Subject]:
        return self._repository.list_by_tenant(tenant_id, search)
