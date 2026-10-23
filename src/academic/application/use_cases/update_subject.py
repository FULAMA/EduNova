from uuid import UUID

from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.subject import Subject


class UpdateSubject:
    def __init__(self, repository: SubjectRepository):
        self._repository = repository

    def execute(
        self, tenant_id: UUID, subject_id: UUID, name: str, code: str,
    ) -> Subject:
        existing = self._repository.find_by_id(subject_id, tenant_id)
        if existing is None:
            raise LookupError("Matière introuvable.")
        updated = Subject(
            existing.id, tenant_id, name.strip(), code.strip(), existing.coefficient,
            existing.active,
        )
        self._repository.update(updated)
        return updated
