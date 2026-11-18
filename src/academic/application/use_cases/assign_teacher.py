from datetime import datetime, timezone
from uuid import UUID

from src.academic.application.interfaces.academic_class_repository import AcademicClassRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.application.interfaces.teacher_assignment_repository import TeacherAssignmentRepository
from src.academic.domain.entities.academic_year import AcademicYearStatus
from src.academic.domain.entities.teacher_assignment import TeacherAssignment
from src.tenancy.application.interfaces.membership_repository import MembershipRepository


class AssignTeacher:
    def __init__(
        self,
        teacher_assignment_repository: TeacherAssignmentRepository,
        membership_repository: MembershipRepository,
        class_repository: AcademicClassRepository,
        subject_repository: SubjectRepository,
        year_repository: AcademicYearRepository,
    ):
        self._assignments = teacher_assignment_repository
        self._memberships = membership_repository
        self._classes = class_repository
        self._subjects = subject_repository
        self._years = year_repository

    def execute(
        self,
        tenant_id: UUID,
        teacher_user_id: UUID,
        academic_class_id: UUID,
        subject_id: UUID,
        academic_year_id: UUID,
        assigned_by: UUID,
    ) -> TeacherAssignment:
        membership = self._memberships.find_by_user_and_tenant(teacher_user_id, tenant_id)
        if (
            membership is None
            or not membership.active
            or membership.role not in {"PROF", "TEACHER"}
        ):
            raise ValueError("L'utilisateur n'est pas un enseignant actif de cet etablissement.")

        if self._classes.find_by_id(academic_class_id, tenant_id) is None:
            raise ValueError("Classe introuvable dans cet etablissement.")

        if self._subjects.find_by_id(subject_id, tenant_id) is None:
            raise ValueError("Matiere introuvable dans cet etablissement.")

        year = self._years.find_by_id(academic_year_id, tenant_id)
        if year is None:
            raise ValueError("Annee scolaire introuvable dans cet etablissement.")
        if year.status is AcademicYearStatus.CLOSED:
            raise ValueError("Impossible d'affecter un enseignant a une annee scolaire cloturee.")

        assignment = TeacherAssignment(
            tenant_id=tenant_id,
            teacher_user_id=teacher_user_id,
            academic_class_id=academic_class_id,
            subject_id=subject_id,
            academic_year_id=academic_year_id,
            assigned_by=assigned_by,
            assigned_at=datetime.now(timezone.utc),
        )
        return self._assignments.save(assignment)
