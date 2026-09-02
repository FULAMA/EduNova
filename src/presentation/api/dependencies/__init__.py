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
from src.application.use_cases.enable_two_factor import (
    EnableTwoFactor,
)
from src.application.use_cases.login_user import (
    LoginUser,
)
from src.application.use_cases.refresh_access_token import (
    RefreshAccessToken,
)
from src.application.use_cases.register_user import (
    RegisterUser,
)
from src.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.application.use_cases.verify_two_factor import (
    VerifyTwoFactor,
)
from src.presentation.api.container import ApplicationContainer


container = ApplicationContainer()


def get_analyze_student_academic_record_use_case(
) -> AnalyzeStudentAcademicRecord:
    return container.analyze_student_academic_record()


def get_add_subject_result_use_case() -> AddSubjectResult:
    return container.add_subject_result()


def get_create_academic_record_use_case() -> CreateAcademicRecord:
    return container.create_academic_record()


def get_assign_subject_to_class_use_case() -> AssignSubjectToClass:
    return container.assign_subject_to_class()


def get_analyze_academic_risk_use_case() -> AnalyzeAcademicRisk:
    return container.analyze_academic_risk()


def get_enable_two_factor_use_case() -> EnableTwoFactor:
    return container.enable_two_factor()


def get_verify_two_factor_use_case() -> VerifyTwoFactor:
    return container.verify_two_factor()


def get_register_user_use_case() -> RegisterUser:
    return container.register_user()


def get_login_user_use_case() -> LoginUser:
    return container.login_user()


def get_verify_login_two_factor_use_case(
) -> VerifyLoginTwoFactor:
    return container.verify_login_two_factor()


def get_refresh_access_token_use_case() -> RefreshAccessToken:
    return container.refresh_access_token()
