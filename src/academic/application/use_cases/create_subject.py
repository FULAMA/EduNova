from uuid import UUID, uuid4

from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.subject import Subject


class CreateSubject:
    def __init__(self, repository: SubjectRepository):
        self._repository = repository

    def execute(
        self, tenant_id: UUID, name: str, code: str, coefficient: float,
    ) -> Subject:
        subject = Subject(uuid4(), tenant_id, name.strip(), code.strip(), coefficient)
        self._repository.save(subject)
        return subject
