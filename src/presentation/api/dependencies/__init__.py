from src.academic.application.use_cases.add_subject_result import AddSubjectResult
from src.academic.application.use_cases.analyze_academic_risk import (
    AnalyzeAcademicRisk,
)
from src.academic.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.academic.application.use_cases.assign_subject_to_class import (
    AssignSubjectToClass,
)
from src.academic.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.identity.application.use_cases.enable_two_factor import (
    EnableTwoFactor,
)
from src.identity.application.use_cases.login_user import (
    LoginUser,
)
from src.identity.application.use_cases.refresh_access_token import (
    RefreshAccessToken,
)
from src.identity.application.use_cases.register_user import (
    RegisterUser,
)
from src.identity.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.identity.application.use_cases.verify_two_factor import (
    VerifyTwoFactor,
)
from src.identity.application.interfaces.user_repository import UserRepository
from src.tenancy.application.interfaces.tenant_repository import TenantRepository
from src.tenancy.application.interfaces.membership_repository import MembershipRepository
from src.presentation.api.container import ApplicationContainer


_container: ApplicationContainer | None = None


def get_container() -> ApplicationContainer:
    global _container

    if _container is None:
        _container = ApplicationContainer()

    return _container


def get_jwt_service():
    return get_container()._jwt_service()

def get_user_repository() -> UserRepository:
    return get_container()._user_repository()


def get_tenant_repository() -> TenantRepository:
    return get_container()._tenant_repository()


def get_membership_repository() -> MembershipRepository:
    return get_container()._membership_repository()


def get_analyze_student_academic_record_use_case(
) -> AnalyzeStudentAcademicRecord:
    return get_container().analyze_student_academic_record()


def get_add_subject_result_use_case() -> AddSubjectResult:
    return get_container().add_subject_result()


def get_create_academic_record_use_case() -> CreateAcademicRecord:
    return get_container().create_academic_record()


def get_assign_subject_to_class_use_case() -> AssignSubjectToClass:
    return get_container().assign_subject_to_class()


def get_analyze_academic_risk_use_case() -> AnalyzeAcademicRisk:
    return get_container().analyze_academic_risk()


def get_enable_two_factor_use_case() -> EnableTwoFactor:
    return get_container().enable_two_factor()


def get_login_user_use_case() -> LoginUser:
    return get_container().login_user()


def get_refresh_access_token_use_case() -> RefreshAccessToken:
    return get_container().refresh_access_token()


def get_register_user_use_case() -> RegisterUser:
    return get_container().register_user()


def get_verify_login_two_factor_use_case() -> VerifyLoginTwoFactor:
    return get_container().verify_login_two_factor()


def get_verify_two_factor_use_case() -> VerifyTwoFactor:
    return get_container().verify_two_factor()
