from copy import deepcopy
from uuid import UUID

from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.exceptions import AcademicRecordConcurrencyError
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
        self._history: list[dict] = []

    def save(
        self,
        record: StudentAcademicRecord,
        *,
        expected_version: int | None = None,
        operation: str = "SAVE",
        actor_id: UUID | None = None,
        reason: str | None = None,
    ) -> None:
        key = (
            record.tenant_id,
            record.student_id,
            record.academic_period_id,
        )

        current = self._records.get(key)
        if expected_version is None and current is not None:
            raise ValueError("Academic record already exists")
        if expected_version is not None:
            if current is None or current["version"] != expected_version:
                raise AcademicRecordConcurrencyError(
                    "Le dossier académique a été modifié. Rechargez-le avant de réessayer."
                )

        snapshot = StudentAcademicRecordMapper.to_dict(record)
        self._records[key] = snapshot
        self._history.append({
            "tenant_id": str(record.tenant_id),
            "student_id": str(record.student_id),
            "academic_period_id": str(record.academic_period_id),
            "version": record.version,
            "operation": operation,
            "actor_id": str(actor_id) if actor_id is not None else None,
            "reason": reason,
            "snapshot": deepcopy(snapshot),
        })

    @property
    def history(self) -> tuple[dict, ...]:
        return tuple(deepcopy(entry) for entry in self._history)

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

    def list_history(self, student_id, academic_period_id, tenant_id):
        return tuple(
            deepcopy(entry)
            for entry in self._history
            if entry["student_id"] == str(student_id)
            and entry["academic_period_id"] == str(academic_period_id)
            and entry["tenant_id"] == str(tenant_id)
        )
