from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.academic.domain.entities.attendance import AttendanceStatus


class AttendanceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    student_id: UUID
    academic_class_id: UUID
    academic_year_id: UUID
    academic_period_id: UUID
    attendance_date: date
    status: AttendanceStatus
    justified: bool = False


class AttendanceRosterEntryResponse(BaseModel):
    student_id: UUID
    first_name: str
    last_name: str
    status: AttendanceStatus | None
    justified: bool


class AttendanceResponse(BaseModel):
    id: UUID
    student_id: UUID
    academic_class_id: UUID
    academic_year_id: UUID
    academic_period_id: UUID
    attendance_date: date
    status: AttendanceStatus
    justified: bool
    recorded_by: UUID | None
    version: int


class AttendanceCorrectionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: AttendanceStatus
    justified: bool = False
    expected_version: int


class AttendanceStatisticsResponse(BaseModel):
    total_sessions: int
    absences: int
    justified_absences: int
    unjustified_absences: int
    lates: int
    attendance_rate: float | None
