from uuid import UUID

from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository


class ListStudentAcademicPeriods:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
        period_repository: AcademicPeriodRepository | None = None,
    ):
        self._repository = repository
        self._period_repository = period_repository

    def execute(self, student_id: UUID, tenant_id: UUID) -> tuple[UUID, ...]:
        return self._repository.list_period_ids_by_student(student_id, tenant_id)

    def execute_detailed(
        self, student_id: UUID, tenant_id: UUID
    ) -> list[dict[str, UUID | str | None]]:
        period_ids = self.execute(student_id, tenant_id)
        periods = {
            period.id: period
            for period in self._period_repository.list_by_tenant(tenant_id)
        } if self._period_repository is not None else {}
        return [
            {"id": period_id, "name": periods[period_id].name if period_id in periods else None}
            for period_id in period_ids
        ]
