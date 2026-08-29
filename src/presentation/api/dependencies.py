from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.presentation.api.container import ApplicationContainer


container = ApplicationContainer()


def get_use_case() -> AnalyzeStudentAcademicRecord:
    return container.analyze_student_academic_record()
