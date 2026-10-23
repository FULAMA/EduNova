from uuid import UUID

from src.academic.application.exceptions import ActiveConflictError
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.domain.entities.academic_year import AcademicYearStatus
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus


class ChangeStudentAssignmentStatus:
    def __init__(self, assignments: StudentAssignmentRepository, years: AcademicYearRepository):
        self._assignments = assignments
        self._years = years

    def activate(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment:
        assignment = self._get(assignment_id, tenant_id)
        year = self._years.find_by_id(assignment.academic_year_id, tenant_id)
        if year is None or year.status is not AcademicYearStatus.ACTIVE:
            raise ValueError("Une affectation exige une annee scolaire active.")
        existing_assignments = self._assignments.list_by_student(assignment.student_id, tenant_id)
        if any(
            a.academic_year_id == assignment.academic_year_id
            and a.status is StudentAssignmentStatus.ACTIVE
            and a.id != assignment.id
            for a in existing_assignments
        ):
            raise ActiveConflictError("Une affectation active existe deja pour cet eleve et cette annee.")
        activated = assignment.activate()
        return self._assignments.update(activated, StudentAssignmentStatus.DRAFT.value)

    def cancel(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment:
        assignment = self._get(assignment_id, tenant_id)
        cancelled = assignment.cancel()
        return self._assignments.update(cancelled, StudentAssignmentStatus.DRAFT.value)

    def close(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment:
        assignment = self._get(assignment_id, tenant_id)
        closed = assignment.close()
        return self._assignments.update(closed, StudentAssignmentStatus.ACTIVE.value)

    def _get(self, assignment_id: UUID, tenant_id: UUID) -> StudentAssignment:
        assignment = self._assignments.find_by_id(assignment_id, tenant_id)
        if assignment is None:
            raise ValueError("Affectation introuvable.")
        return assignment
