from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.student_assignment import StudentAssignment


class StudentAssignmentRepository(ABC):
    @abstractmethod
    def save(self, assignment: StudentAssignment) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_student(self, student_id: UUID, tenant_id: UUID) -> tuple[StudentAssignment, ...]:
        raise NotImplementedError

    @abstractmethod
    def update(self, assignment: StudentAssignment, expected_status: str) -> StudentAssignment:
        raise NotImplementedError
