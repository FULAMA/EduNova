from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)


class ApplicationContainer:
    def __init__(self, database_path: str = "edunova.db"):
        self._database = SQLiteDatabase(database_path)
        self._database.initialize()

    def analyze_student_academic_record(
        self,
    ) -> AnalyzeStudentAcademicRecord:
        repository = SQLiteStudentAcademicRecordRepository(
            self._database
        )

        return AnalyzeStudentAcademicRecord(repository)
