from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.academic.domain.entities.attendance import Attendance


class AttendanceRepository(ABC):
    @abstractmethod
    def record(self, attendance: Attendance) -> Attendance:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, tenant_id: UUID, attendance_id: UUID) -> Attendance | None:
        raise NotImplementedError

    @abstractmethod
    def correct(self, attendance: Attendance, expected_version: int, changed_by: UUID) -> Attendance:
        raise NotImplementedError

    @abstractmethod
    def list_by_class_date(
        self, tenant_id: UUID, academic_class_id: UUID,
        academic_period_id: UUID, attendance_date: date,
    ) -> tuple[Attendance, ...]:
        raise NotImplementedError

    @abstractmethod
    def list_by_student_period(
        self, tenant_id: UUID, student_id: UUID,
        academic_period_id: UUID,
    ) -> tuple[Attendance, ...]:
        raise NotImplementedError

    @abstractmethod
    def has_active_assignment(
        self, tenant_id: UUID, student_id: UUID,
        academic_class_id: UUID, academic_year_id: UUID,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_active_roster(self, tenant_id: UUID, academic_class_id: UUID,
                           academic_year_id: UUID):
        raise NotImplementedError
