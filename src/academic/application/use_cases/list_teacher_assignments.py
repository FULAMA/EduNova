from uuid import UUID

from src.academic.application.interfaces.teacher_assignment_repository import TeacherAssignmentRepository
from src.academic.domain.entities.teacher_assignment import TeacherAssignment


class ListTeacherAssignments:
    def __init__(self, teacher_assignment_repository: TeacherAssignmentRepository):
        self._repository = teacher_assignment_repository

    def execute_for_teacher(
        self, tenant_id: UUID, teacher_user_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignment, ...]:
        return self._repository.list_by_teacher(tenant_id, teacher_user_id, academic_year_id)

    def execute_for_class(
        self, tenant_id: UUID, academic_class_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignment, ...]:
        return self._repository.list_by_class(tenant_id, academic_class_id, academic_year_id)
