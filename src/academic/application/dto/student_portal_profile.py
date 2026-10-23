from dataclasses import dataclass
from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.domain.entities.academic_year import AcademicYear
from src.academic.domain.entities.student_assignment import StudentAssignment


@dataclass(frozen=True)
class StudentPortalProfile:
    student: StudentSummary
    assignment: StudentAssignment | None
    academic_year: AcademicYear | None

