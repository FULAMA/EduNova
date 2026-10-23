from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import (
    StudentRepository,
)


class ListStudents:
    def __init__(self, repository: StudentRepository):
        self._repository = repository

    def execute(self, tenant_id: UUID) -> tuple[StudentSummary, ...]:
        return self._repository.list_by_tenant(tenant_id)
