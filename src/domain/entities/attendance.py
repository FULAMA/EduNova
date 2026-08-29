from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"


@dataclass(frozen=True)
class Attendance:
    id: UUID
    student_id: UUID
    academic_period_id: UUID
    attendance_date: date
    status: AttendanceStatus
    justified: bool = False

    def __post_init__(self):
        if self.status == AttendanceStatus.PRESENT and self.justified:
            raise ValueError(
                "Une présence ne peut pas être justifiée."
            )

    @property
    def is_absent(self) -> bool:
        return self.status == AttendanceStatus.ABSENT

    @property
    def is_late(self) -> bool:
        return self.status == AttendanceStatus.LATE