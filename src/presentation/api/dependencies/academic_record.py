from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)


def get_database() -> SQLiteDatabase:
    database = SQLiteDatabase("edunova.db")
    database.initialize()
    return database


def get_analyze_student_academic_record_use_case() -> AnalyzeStudentAcademicRecord:
    database = get_database()
    repository = SQLiteStudentAcademicRecordRepository(database)

    return AnalyzeStudentAcademicRecord(repository)
