from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AnalyzeStudentAcademicRecordRequest:
    student_id: UUID
    academic_period_id: UUID
