from uuid import UUID

from src.academic.application.dto.student_portal_profile import StudentPortalProfile
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.application.interfaces.student_repository import StudentRepository
from src.identity.application.interfaces.student_user_link_repository import StudentUserLinkRepository
from src.academic.domain.entities.student_assignment import StudentAssignmentStatus


class GetStudentPortalProfile:
    def __init__(
        self,
        links: StudentUserLinkRepository,
        students: StudentRepository,
        assignments: StudentAssignmentRepository,
        years: AcademicYearRepository,
    ):
        self._links = links
        self._students = students
        self._assignments = assignments
        self._years = years

    def execute(self, user_id: UUID, tenant_id: UUID) -> StudentPortalProfile:
        links = self._links.find_by_user(user_id, tenant_id)
        if not links:
            raise ValueError("Aucun dossier eleve n est associe a ce compte.")
        if len(links) > 1:
            raise ValueError("Plusieurs dossiers eleve sont associes a ce compte.")

        student = self._students.get_by_id_and_tenant(links[0].student_id, tenant_id)
        if student is None:
            raise ValueError("Le dossier eleve associe est indisponible.")
        active = tuple(
            item for item in self._assignments.list_by_student(student.id, tenant_id)
            if item.status is StudentAssignmentStatus.ACTIVE
        )
        if len(active) > 1:
            raise ValueError("Plusieurs affectations actives sont associees au dossier.")
        assignment = active[0] if active else None
        year = self._years.find_by_id(assignment.academic_year_id, tenant_id) if assignment else None
        return StudentPortalProfile(student=student, assignment=assignment, academic_year=year)

