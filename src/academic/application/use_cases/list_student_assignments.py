from uuid import UUID

from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.domain.entities.student_assignment import StudentAssignment


class ListStudentAssignments:
    def __init__(self, repository: StudentAssignmentRepository):
        self._repository = repository

    def execute(self, student_id: UUID, tenant_id: UUID) -> tuple[StudentAssignment, ...]:
        return self._repository.list_by_student(student_id, tenant_id)
