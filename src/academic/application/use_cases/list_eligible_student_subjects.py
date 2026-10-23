from dataclasses import dataclass
from uuid import UUID

from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.class_subject_repository import ClassSubjectRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.student_assignment import StudentAssignmentStatus


@dataclass(frozen=True)
class EligibleStudentSubject:
    id: UUID
    name: str
    coefficient: float


class ListEligibleStudentSubjects:
    def __init__(self, assignments: StudentAssignmentRepository,
                 periods: AcademicPeriodRepository,
                 class_subjects: ClassSubjectRepository,
                 subjects: SubjectRepository):
        self._assignments = assignments
        self._periods = periods
        self._class_subjects = class_subjects
        self._subjects = subjects

    def execute(self, student_id: UUID, period_id: UUID, tenant_id: UUID) -> tuple[EligibleStudentSubject, ...]:
        period = self._periods.find_by_id(period_id, tenant_id)
        if period is None or period.academic_year_id is None:
            raise ValueError("Periode introuvable ou non rattachee a une annee scolaire.")
        assignment = next((
            item for item in self._assignments.list_by_student(student_id, tenant_id)
            if item.status is StudentAssignmentStatus.ACTIVE
            and item.academic_year_id == period.academic_year_id
        ), None)
        if assignment is None:
            raise ValueError("Aucune affectation active ne correspond a cette periode.")

        result: list[EligibleStudentSubject] = []
        for class_subject in self._class_subjects.find_by_class_and_option(
            assignment.academic_class_id, assignment.academic_option_id, tenant_id
        ):
            subject = self._subjects.find_by_id(class_subject.subject_id, tenant_id)
            if class_subject.active and subject is not None and subject.active:
                result.append(EligibleStudentSubject(
                    id=subject.id, name=subject.name, coefficient=class_subject.coefficient
                ))
        return tuple(result)
