from fastapi import FastAPI

from src.application.use_cases.add_subject_result import AddSubjectResult
from src.application.use_cases.analyze_academic_risk import AnalyzeAcademicRisk
from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.application.use_cases.assign_subject_to_class import (
    AssignSubjectToClass,
)
from src.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.application.use_cases.enable_two_factor import EnableTwoFactor
from src.application.use_cases.login_user import LoginUser
from src.application.use_cases.refresh_access_token import RefreshAccessToken
from src.application.use_cases.register_user import RegisterUser
from src.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.application.use_cases.verify_two_factor import VerifyTwoFactor

from src.presentation.api.container import ApplicationContainer
from src.presentation.api.dependencies.auth import (
    get_application_container,
)
from src.presentation.api.dependencies import (
    get_add_subject_result_use_case,
    get_analyze_academic_risk_use_case,
    get_analyze_student_academic_record_use_case,
    get_assign_subject_to_class_use_case,
    get_create_academic_record_use_case,
    get_enable_two_factor_use_case,
    get_login_user_use_case,
    get_refresh_access_token_use_case,
    get_register_user_use_case,
    get_verify_login_two_factor_use_case,
    get_verify_two_factor_use_case,
)

from src.presentation.api.routes.academic_records import (
    router as academic_records_router,
)
from src.presentation.api.routes.academic_risk import (
    router as academic_risk_router,
)
from src.presentation.api.routes.auth import router as auth_router
from src.presentation.api.routes.classes import router as classes_router


def create_app(
    container: ApplicationContainer | None = None,
    analyze_student_academic_record_use_case: AnalyzeStudentAcademicRecord | None = None,
    add_subject_result_use_case: AddSubjectResult | None = None,
    create_academic_record_use_case: CreateAcademicRecord | None = None,
    assign_subject_to_class_use_case: AssignSubjectToClass | None = None,
    analyze_academic_risk_use_case: AnalyzeAcademicRisk | None = None,
    enable_two_factor_use_case: EnableTwoFactor | None = None,
    verify_two_factor_use_case: VerifyTwoFactor | None = None,
    verify_login_two_factor_use_case: VerifyLoginTwoFactor | None = None,
    register_user_use_case: RegisterUser | None = None,
    login_user_use_case: LoginUser | None = None,
    refresh_access_token_use_case: RefreshAccessToken | None = None,
) -> FastAPI:

    if container is None:
        container = ApplicationContainer()

    app = FastAPI(
        title="EduNova API",
        description="API REST du systeme academique EduNova",
        version="1.0.0",
    )

    app.dependency_overrides[
        get_application_container
    ] = lambda: container

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "application": "EduNova",
        }

    if analyze_student_academic_record_use_case is not None:
        app.dependency_overrides[
            get_analyze_student_academic_record_use_case
        ] = lambda: analyze_student_academic_record_use_case
    else:
        app.dependency_overrides[
            get_analyze_student_academic_record_use_case
        ] = container.analyze_student_academic_record

    if add_subject_result_use_case is not None:
        app.dependency_overrides[
            get_add_subject_result_use_case
        ] = lambda: add_subject_result_use_case
    else:
        app.dependency_overrides[
            get_add_subject_result_use_case
        ] = container.add_subject_result

    if create_academic_record_use_case is not None:
        app.dependency_overrides[
            get_create_academic_record_use_case
        ] = lambda: create_academic_record_use_case
    else:
        app.dependency_overrides[
            get_create_academic_record_use_case
        ] = container.create_academic_record

    if assign_subject_to_class_use_case is not None:
        app.dependency_overrides[
            get_assign_subject_to_class_use_case
        ] = lambda: assign_subject_to_class_use_case
    else:
        app.dependency_overrides[
            get_assign_subject_to_class_use_case
        ] = container.assign_subject_to_class

    if analyze_academic_risk_use_case is not None:
        app.dependency_overrides[
            get_analyze_academic_risk_use_case
        ] = lambda: analyze_academic_risk_use_case
    else:
        app.dependency_overrides[
            get_analyze_academic_risk_use_case
        ] = container.analyze_academic_risk

    if enable_two_factor_use_case is not None:
        app.dependency_overrides[
            get_enable_two_factor_use_case
        ] = lambda: enable_two_factor_use_case
    else:
        app.dependency_overrides[
            get_enable_two_factor_use_case
        ] = container.enable_two_factor

    if verify_two_factor_use_case is not None:
        app.dependency_overrides[
            get_verify_two_factor_use_case
        ] = lambda: verify_two_factor_use_case
    else:
        app.dependency_overrides[
            get_verify_two_factor_use_case
        ] = container.verify_two_factor

    if verify_login_two_factor_use_case is not None:
        app.dependency_overrides[
            get_verify_login_two_factor_use_case
        ] = lambda: verify_login_two_factor_use_case
    else:
        app.dependency_overrides[
            get_verify_login_two_factor_use_case
        ] = container.verify_login_two_factor

    if register_user_use_case is not None:
        app.dependency_overrides[
            get_register_user_use_case
        ] = lambda: register_user_use_case
    else:
        app.dependency_overrides[
            get_register_user_use_case
        ] = container.register_user

    if login_user_use_case is not None:
        app.dependency_overrides[
            get_login_user_use_case
        ] = lambda: login_user_use_case
    else:
        app.dependency_overrides[
            get_login_user_use_case
        ] = container.login_user

    if refresh_access_token_use_case is not None:
        app.dependency_overrides[
            get_refresh_access_token_use_case
        ] = lambda: refresh_access_token_use_case
    else:
        app.dependency_overrides[
            get_refresh_access_token_use_case
        ] = container.refresh_access_token

    app.include_router(academic_records_router)
    app.include_router(classes_router)
    app.include_router(academic_risk_router)
    app.include_router(auth_router)

    return app


app = create_app()
