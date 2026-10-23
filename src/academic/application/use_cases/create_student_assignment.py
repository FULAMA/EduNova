from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.academic.application.interfaces.academic_class_repository import AcademicClassRepository
from src.academic.application.interfaces.academic_option_repository import AcademicOptionRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.class_option_repository import ClassOptionRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.domain.entities.academic_year import AcademicYearStatus
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus


class CreateStudentAssignment:
    def __init__(
        self,
        assignment_repository: StudentAssignmentRepository,
        student_repository: StudentRepository,
        class_repository: AcademicClassRepository,
        year_repository: AcademicYearRepository,
        option_repository: AcademicOptionRepository,
        class_option_repository: ClassOptionRepository,
    ):
        self._assignments = assignment_repository
        self._students = student_repository
        self._classes = class_repository
        self._years = year_repository
        self._options = option_repository
        self._class_options = class_option_repository

    def execute(
        self,
        tenant_id: UUID,
        student_id: UUID,
        academic_year_id: UUID,
        academic_class_id: UUID,
        created_by: UUID,
        academic_option_id: UUID | None = None,
    ) -> StudentAssignment:
        if self._students.get_by_id_and_tenant(student_id, tenant_id) is None:
            raise ValueError("Eleve introuvable dans cet etablissement.")
        if self._classes.find_by_id(academic_class_id, tenant_id) is None:
            raise ValueError("Classe introuvable dans cet etablissement.")
        year = self._years.find_by_id(academic_year_id, tenant_id)
        if year is None:
            raise ValueError("Annee scolaire introuvable.")
        if year.status is AcademicYearStatus.CLOSED:
            raise ValueError("Une affectation ne peut pas etre creee dans une annee cloturee.")
        if academic_option_id is not None:
            if self._options.find_by_id(academic_option_id, tenant_id) is None:
                raise ValueError("Option introuvable dans cet etablissement.")
            if self._class_options.find_by_class_and_option(
                academic_class_id, academic_option_id, tenant_id
            ) is None:
                raise ValueError("L'option n'est pas associee a cette classe.")

        now = datetime.now(timezone.utc)
        assignment = StudentAssignment(
            id=uuid4(), tenant_id=tenant_id, student_id=student_id,
            academic_year_id=academic_year_id, academic_class_id=academic_class_id,
            academic_option_id=academic_option_id,
            status=StudentAssignmentStatus.DRAFT, created_by=created_by,
            created_at=now, updated_at=now,
        )
        self._assignments.save(assignment)
        return assignment
