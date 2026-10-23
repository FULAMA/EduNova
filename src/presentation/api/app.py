import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.academic.application.use_cases.add_subject_result import AddSubjectResult
from src.academic.application.use_cases.analyze_academic_risk import AnalyzeAcademicRisk
from src.academic.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.academic.application.use_cases.assign_subject_to_class import (
    AssignSubjectToClass,
)
from src.academic.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.academic.application.use_cases.list_students import ListStudents
from src.academic.application.use_cases.get_student import GetStudent
from src.identity.application.use_cases.enable_two_factor import EnableTwoFactor
from src.identity.application.use_cases.login_user import LoginUser
from src.identity.application.use_cases.login_with_google import LoginWithGoogle
from src.identity.application.use_cases.link_google_identity import LinkGoogleIdentity
from src.identity.application.use_cases.refresh_access_token import RefreshAccessToken
from src.identity.application.use_cases.register_user import RegisterUser
from src.identity.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.identity.application.use_cases.verify_two_factor import VerifyTwoFactor

from src.presentation.api.container import ApplicationContainer
from src.presentation.api.dependencies import (
    get_add_subject_result_use_case,
    get_analyze_academic_risk_use_case,
    get_analyze_student_academic_record_use_case,
    get_assign_subject_to_class_use_case,
    get_create_academic_record_use_case,
    get_validate_academic_record_use_case,
    get_correct_academic_record_use_case,
    get_student_academic_record_repository,
    get_enable_two_factor_use_case,
    get_jwt_service,
    get_membership_repository,
    get_tenant_repository,
    get_user_repository,
    get_login_user_use_case,
    get_login_with_google_use_case,
    get_link_google_identity_use_case,
    get_list_students_use_case,
    get_list_student_academic_periods_use_case,
    get_list_eligible_student_periods_use_case,
    get_list_eligible_student_subjects_use_case,
    get_list_subjects_use_case,
    get_create_subject_use_case,
    get_update_subject_use_case,
    get_list_academic_periods_use_case,
    get_create_academic_period_use_case,
    get_list_academic_classes_use_case,
    get_create_academic_year_use_case,
    get_list_academic_years_use_case,
    get_change_academic_year_status_use_case,
    get_create_student_assignment_use_case,
    get_list_student_assignments_use_case,
    get_change_student_assignment_status_use_case,
    get_record_attendance_use_case,
    get_list_class_attendance_use_case,
    get_get_attendance_statistics_use_case,
    get_correct_attendance_use_case,
    get_analyze_student_academic_risk_use_case,
    get_list_student_attendance_use_case,
    get_billing_service,
    get_prepare_deliberation_use_case,
    get_apply_student_promotion_use_case,
    get_validate_deliberation_use_case,
    get_get_student_use_case,
    get_refresh_access_token_use_case,
    get_register_user_use_case,
    get_verify_login_two_factor_use_case,
    get_verify_two_factor_use_case,
    get_link_student_account_use_case,
    get_student_portal_profile_use_case,
    get_prepare_report_card_use_case,
    get_publish_report_card_use_case,
    get_list_student_report_cards_use_case,
    get_student_report_card_use_case,
    get_correct_report_card_use_case,
)

from src.presentation.api.routes.academic_records import (
    router as academic_records_router,
)
from src.presentation.api.routes.academic_catalogues import router as academic_catalogues_router
from src.presentation.api.routes.academic_risk import (
    router as academic_risk_router,
)
from src.presentation.api.routes.auth import router as auth_router
from src.presentation.api.routes.classes import router as classes_router
from src.presentation.api.routes.students import router as students_router
from src.presentation.api.routes.academic_years import router as academic_years_router
from src.presentation.api.routes.student_assignments import router as student_assignments_router
from src.presentation.api.routes.attendance import router as attendance_router
from src.presentation.api.routes.billing import router as billing_router
from src.presentation.api.routes.student_portal import router as student_portal_router
from src.presentation.api.routes.report_cards import router as report_cards_router


def create_app(
    container: ApplicationContainer | None = None,
    database_path: str = ":memory:",
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
    login_with_google_use_case: LoginWithGoogle | None = None,
    link_google_identity_use_case: LinkGoogleIdentity | None = None,
    refresh_access_token_use_case: RefreshAccessToken | None = None,
    list_students_use_case: ListStudents | None = None,
    get_student_use_case: GetStudent | None = None,
) -> FastAPI:

    if container is None:
        if database_path == ":memory:":
            database_path = os.getenv(
                "EDUNOVA_DATABASE_PATH",
                database_path,
            )
        container = ApplicationContainer(database_path=database_path)

    app = FastAPI(
        title="EduNova API",
        description="API REST du systeme academique EduNova",
        version="1.0.0",
        docs_url=None if container._settings.environment == "production" else "/docs",
        redoc_url=None if container._settings.environment == "production" else "/redoc",
        openapi_url=None if container._settings.environment == "production" else "/openapi.json",
    )

    app.dependency_overrides[get_jwt_service] = container._jwt_service
    app.dependency_overrides[get_user_repository] = container._user_repository
    app.dependency_overrides[get_tenant_repository] = container._tenant_repository
    app.dependency_overrides[get_membership_repository] = container._membership_repository
    app.dependency_overrides[get_link_student_account_use_case] = container.link_student_account
    app.dependency_overrides[get_student_portal_profile_use_case] = container.get_student_portal_profile
    app.dependency_overrides[get_prepare_report_card_use_case] = container.prepare_report_card
    app.dependency_overrides[get_publish_report_card_use_case] = container.publish_report_card
    app.dependency_overrides[get_list_student_report_cards_use_case] = container.list_student_report_cards
    app.dependency_overrides[get_student_report_card_use_case] = container.get_student_report_card
    app.dependency_overrides[get_correct_report_card_use_case] = container.correct_report_card

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(container._settings.cors_allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def add_security_headers(
        request: Request,
        call_next,
    ):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        if container._settings.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
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

    app.dependency_overrides[
        get_validate_academic_record_use_case
    ] = container.validate_academic_record
    app.dependency_overrides[
        get_correct_academic_record_use_case
    ] = container.correct_academic_record

    if list_students_use_case is not None:
        app.dependency_overrides[
            get_list_students_use_case
        ] = lambda: list_students_use_case
    else:
        app.dependency_overrides[
            get_list_students_use_case
        ] = container.list_students

    app.dependency_overrides[
        get_list_student_academic_periods_use_case
    ] = container.list_student_academic_periods
    app.dependency_overrides[get_list_eligible_student_periods_use_case] = container.list_eligible_student_periods
    app.dependency_overrides[get_list_eligible_student_subjects_use_case] = container.list_eligible_student_subjects
    app.dependency_overrides[get_list_subjects_use_case] = container.list_subjects
    app.dependency_overrides[get_create_subject_use_case] = container.create_subject
    app.dependency_overrides[get_update_subject_use_case] = container.update_subject
    app.dependency_overrides[get_list_academic_periods_use_case] = container.list_academic_periods
    app.dependency_overrides[get_create_academic_period_use_case] = container.create_academic_period
    app.dependency_overrides[get_list_academic_classes_use_case] = container.list_academic_classes
    app.dependency_overrides[get_create_academic_year_use_case] = container.create_academic_year
    app.dependency_overrides[get_list_academic_years_use_case] = container.list_academic_years
    app.dependency_overrides[get_change_academic_year_status_use_case] = container.change_academic_year_status
    app.dependency_overrides[get_create_student_assignment_use_case] = container.create_student_assignment
    app.dependency_overrides[get_list_student_assignments_use_case] = container.list_student_assignments
    app.dependency_overrides[get_change_student_assignment_status_use_case] = container.change_student_assignment_status
    app.dependency_overrides[get_student_academic_record_repository] = container._student_academic_record_repository

    if get_student_use_case is not None:
        app.dependency_overrides[
            get_get_student_use_case
        ] = lambda: get_student_use_case
    else:
        app.dependency_overrides[
            get_get_student_use_case
        ] = container.get_student

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

    if login_with_google_use_case is not None:
        app.dependency_overrides[
            get_login_with_google_use_case
        ] = lambda: login_with_google_use_case
    else:
        app.dependency_overrides[
            get_login_with_google_use_case
        ] = container.login_with_google

    if link_google_identity_use_case is not None:
        app.dependency_overrides[
            get_link_google_identity_use_case
        ] = lambda: link_google_identity_use_case
    else:
        app.dependency_overrides[
            get_link_google_identity_use_case
        ] = container.link_google_identity

    if refresh_access_token_use_case is not None:
        app.dependency_overrides[
            get_refresh_access_token_use_case
        ] = lambda: refresh_access_token_use_case
    else:
        app.dependency_overrides[
            get_refresh_access_token_use_case
        ] = container.refresh_access_token

    app.include_router(academic_records_router)
    app.include_router(academic_catalogues_router)
    app.include_router(classes_router)
    app.include_router(academic_risk_router)
    app.include_router(auth_router)
    app.include_router(students_router)
    app.include_router(academic_years_router)
    app.include_router(student_assignments_router)
    app.dependency_overrides[get_record_attendance_use_case] = container.record_attendance
    app.dependency_overrides[get_billing_service] = container.billing_service
    app.dependency_overrides[get_list_class_attendance_use_case] = container.list_class_attendance
    app.dependency_overrides[get_get_attendance_statistics_use_case] = container.get_attendance_statistics
    app.dependency_overrides[get_correct_attendance_use_case] = container.correct_attendance
    app.dependency_overrides[get_analyze_student_academic_risk_use_case] = container.analyze_student_academic_risk
    app.dependency_overrides[get_list_student_attendance_use_case] = container.list_student_attendance
    app.dependency_overrides[get_prepare_deliberation_use_case] = container.prepare_deliberation
    app.dependency_overrides[get_apply_student_promotion_use_case] = container.apply_student_promotion
    app.dependency_overrides[get_validate_deliberation_use_case] = container.validate_deliberation
    app.include_router(attendance_router)
    app.include_router(billing_router)
    app.include_router(student_portal_router)
    app.include_router(report_cards_router)

    return app
