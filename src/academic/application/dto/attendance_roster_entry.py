from dataclasses import dataclass
from uuid import UUID

from src.academic.domain.entities.attendance import AttendanceStatus


@dataclass(frozen=True)
class AttendanceRosterEntry:
    student_id: UUID
    first_name: str
    last_name: str
    status: AttendanceStatus | None
    justified: bool
