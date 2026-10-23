from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from src.academic.domain.entities.student_assignment import StudentAssignmentStatus
from src.presentation.api.schemas.attendance import AttendanceResponse, AttendanceStatisticsResponse


class LinkStudentAccountInput(BaseModel):
    user_id: UUID
    student_id: UUID


class StudentPortalStudent(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str | None
    active: bool


class StudentPortalAssignment(BaseModel):
    id: UUID
    academic_year_id: UUID
    academic_class_id: UUID
    status: StudentAssignmentStatus
    created_at: datetime


class StudentPortalYear(BaseModel):
    id: UUID
    label: str
    start_date: date
    end_date: date
    status: str


class StudentPortalResponse(BaseModel):
    student: StudentPortalStudent
    assignment: StudentPortalAssignment | None
    academic_year: StudentPortalYear | None


class StudentPortalAttendanceResponse(BaseModel):
    records: list[AttendanceResponse]
    statistics: AttendanceStatisticsResponse
