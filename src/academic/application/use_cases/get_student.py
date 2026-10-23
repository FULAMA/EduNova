from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import (
    StudentRepository,
)


class GetStudent:
    def __init__(self, repository: StudentRepository):
        self._repository = repository

    def execute(self, student_id: UUID, tenant_id: UUID) -> StudentSummary | None:
        return self._repository.get_by_id_and_tenant(student_id, tenant_id)
