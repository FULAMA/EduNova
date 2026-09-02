from src.application.use_cases.add_subject_result import AddSubjectResult
from src.application.use_cases.analyze_academic_risk import (
    AnalyzeAcademicRisk,
)
from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.application.use_cases.assign_subject_to_class import (
    AssignSubjectToClass,
)
from src.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.domain.services.academic_risk_analyzer import AcademicRiskAnalyzer
from src.infrastructure.persistence.database import SQLiteDatabase
from src.presentation.api.container import ApplicationContainer


def test_container_accepts_injected_database():
    database = SQLiteDatabase(":memory:")

    container = ApplicationContainer(database=database)

    assert container._database is database


def test_container_creates_analyze_student_academic_record():
    database = SQLiteDatabase(":memory:")

    container = ApplicationContainer(database=database)

    use_case = container.analyze_student_academic_record()

    assert isinstance(use_case, AnalyzeStudentAcademicRecord)


def test_container_creates_add_subject_result():
    database = SQLiteDatabase(":memory:")

    container = ApplicationContainer(database=database)

    use_case = container.add_subject_result()

    assert isinstance(use_case, AddSubjectResult)


def test_container_creates_create_academic_record():
    database = SQLiteDatabase(":memory:")

    container = ApplicationContainer(database=database)

    use_case = container.create_academic_record()

    assert isinstance(use_case, CreateAcademicRecord)


def test_container_creates_assign_subject_to_class():
    database = SQLiteDatabase(":memory:")

    container = ApplicationContainer(database=database)

    use_case = container.assign_subject_to_class()

    assert isinstance(use_case, AssignSubjectToClass)


def test_container_creates_analyze_academic_risk():
    database = SQLiteDatabase(":memory:")

    container = ApplicationContainer(database=database)

    use_case = container.analyze_academic_risk()

    assert isinstance(use_case, AnalyzeAcademicRisk)

    assert isinstance(
        use_case._analyzer,
        AcademicRiskAnalyzer,
    )
