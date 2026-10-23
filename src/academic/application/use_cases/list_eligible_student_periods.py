from dataclasses import dataclass
from uuid import UUID

from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.student_academic_record_repository import StudentAcademicRecordRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.domain.entities.student_assignment import StudentAssignmentStatus


@dataclass(frozen=True)
class EligibleStudentPeriod:
    id: UUID
    name: str
    academic_year_id: UUID
    academic_year_label: str
    has_record: bool


class ListEligibleStudentPeriods:
    def __init__(self, assignments: StudentAssignmentRepository,
                 periods: AcademicPeriodRepository,
                 records: StudentAcademicRecordRepository,
                 years: AcademicYearRepository):
        self._assignments = assignments
        self._periods = periods
        self._records = records
        self._years = years

    def execute(self, student_id: UUID, tenant_id: UUID) -> tuple[EligibleStudentPeriod, ...]:
        active_year_ids = {
            assignment.academic_year_id
            for assignment in self._assignments.list_by_student(student_id, tenant_id)
            if assignment.status is StudentAssignmentStatus.ACTIVE
        }
        existing_period_ids = set(self._records.list_period_ids_by_student(student_id, tenant_id))
        result = []
        for period in self._periods.list_by_tenant(tenant_id):
            if period.academic_year_id not in active_year_ids:
                continue
            year = self._years.find_by_id(period.academic_year_id, tenant_id)
            if year is not None:
                result.append(EligibleStudentPeriod(
                    period.id, period.name, period.academic_year_id,
                    year.label, period.id in existing_period_ids,
                ))
        return tuple(result)
