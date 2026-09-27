from uuid import UUID

from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.domain.entities.student_academic_record import StudentAcademicRecord
from src.infrastructure.persistence.student_academic_record_mapper import (
    StudentAcademicRecordMapper,
)


class InMemoryStudentAcademicRecordRepository(
    StudentAcademicRecordRepository
):

    def __init__(self):
        self._records: dict[
            tuple[UUID, UUID, UUID],
            dict,
        ] = {}

    def save(self, record: StudentAcademicRecord) -> None:
        key = (
            record.tenant_id,
            record.student_id,
            record.academic_period_id,
        )

        self._records[key] = StudentAcademicRecordMapper.to_dict(record)

    def find_by_student(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:

        for data in self._records.values():
            if (
                data["tenant_id"] == str(tenant_id)
                and data["student_id"] == str(student_id)
            ):
                return StudentAcademicRecordMapper.to_domain(data)

        return None

    def find_by_student_and_period(
        self,
        student_id: UUID,
        academic_period_id: UUID,
        tenant_id: UUID,
    ) -> StudentAcademicRecord | None:

        key = (
            tenant_id,
            student_id,
            academic_period_id,
        )

        data = self._records.get(key)

        if data is None:
            return None

        return StudentAcademicRecordMapper.to_domain(data)
