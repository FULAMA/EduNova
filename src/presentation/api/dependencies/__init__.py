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
from src.academic.application.use_cases.validate_academic_record import (
    ValidateAcademicRecord,
)
from src.academic.application.use_cases.correct_academic_record import (
    CorrectAcademicRecord,
)
from src.academic.application.use_cases.list_students import ListStudents
from src.academic.application.use_cases.list_student_academic_periods import ListStudentAcademicPeriods
from src.academic.application.use_cases.get_student import GetStudent
from src.academic.application.use_cases.list_subjects import ListSubjects
from src.academic.application.use_cases.create_subject import CreateSubject
from src.academic.application.use_cases.update_subject import UpdateSubject
from src.academic.application.use_cases.list_academic_periods import ListAcademicPeriods
from src.academic.application.use_cases.create_academic_period import CreateAcademicPeriod
from src.academic.application.use_cases.list_eligible_student_periods import ListEligibleStudentPeriods
from src.academic.application.use_cases.list_eligible_student_subjects import ListEligibleStudentSubjects
from src.academic.application.use_cases.list_academic_classes import ListAcademicClasses
from src.academic.application.use_cases.create_academic_year import CreateAcademicYear
from src.academic.application.use_cases.list_academic_years import ListAcademicYears
from src.academic.application.use_cases.change_academic_year_status import ChangeAcademicYearStatus
from src.academic.application.use_cases.create_student_assignment import CreateStudentAssignment
from src.academic.application.use_cases.list_student_assignments import ListStudentAssignments
from src.academic.application.use_cases.record_attendance import RecordAttendance
from src.academic.application.use_cases.list_class_attendance import ListClassAttendance
from src.academic.application.use_cases.get_attendance_statistics import GetAttendanceStatistics
from src.academic.application.use_cases.correct_attendance import CorrectAttendance
from src.academic.application.use_cases.analyze_student_academic_risk import AnalyzeStudentAcademicRisk
from src.academic.application.use_cases.list_student_attendance import ListStudentAttendance
from src.academic.application.use_cases.prepare_deliberation import PrepareDeliberation
from src.academic.application.use_cases.apply_student_promotion import ApplyStudentPromotion
from src.academic.application.use_cases.validate_deliberation import ValidateDeliberation
from src.academic.application.use_cases.prepare_report_card import PrepareReportCard
from src.academic.application.use_cases.publish_report_card import PublishReportCard
from src.academic.application.use_cases.list_student_report_cards import ListStudentReportCards
from src.academic.application.use_cases.get_student_report_card import GetStudentReportCard
from src.academic.application.use_cases.correct_report_card import CorrectReportCard
from src.academic.application.interfaces.report_card_renderer import ReportCardRenderer
from src.infrastructure.rendering.pdf_report_card_renderer import PdfReportCardRenderer
from src.academic.application.use_cases.change_student_assignment_status import ChangeStudentAssignmentStatus
from src.identity.application.use_cases.enable_two_factor import (
    EnableTwoFactor,
)
from src.identity.application.use_cases.login_user import (
    LoginUser,
)
from src.identity.application.use_cases.login_with_google import LoginWithGoogle
from src.identity.application.use_cases.link_google_identity import LinkGoogleIdentity
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
from src.identity.application.use_cases.link_student_account import LinkStudentAccount
from src.identity.application.use_cases.get_student_portal_profile import GetStudentPortalProfile
from src.identity.application.interfaces.user_repository import UserRepository
from src.tenancy.application.interfaces.tenant_repository import TenantRepository
from src.tenancy.application.interfaces.membership_repository import MembershipRepository
from src.presentation.api.container import ApplicationContainer
from src.billing.application.service import BillingService


_container: ApplicationContainer | None = None


def get_container() -> ApplicationContainer:
    global _container

    if _container is None:
        _container = ApplicationContainer()

    return _container


def get_billing_service() -> BillingService:
    return get_container().billing_service()


def get_jwt_service():
    return get_container()._jwt_service()

def get_user_repository() -> UserRepository:
    return get_container()._user_repository()


def get_tenant_repository() -> TenantRepository:
    return get_container()._tenant_repository()


def get_membership_repository() -> MembershipRepository:
    return get_container()._membership_repository()


def get_link_student_account_use_case() -> LinkStudentAccount:
    return get_container().link_student_account()


def get_student_portal_profile_use_case() -> GetStudentPortalProfile:
    return get_container().get_student_portal_profile()


def get_analyze_student_academic_record_use_case(
) -> AnalyzeStudentAcademicRecord:
    return get_container().analyze_student_academic_record()


def get_add_subject_result_use_case() -> AddSubjectResult:
    return get_container().add_subject_result()


def get_create_academic_record_use_case() -> CreateAcademicRecord:
    return get_container().create_academic_record()


def get_validate_academic_record_use_case() -> ValidateAcademicRecord:
    return get_container().validate_academic_record()


def get_correct_academic_record_use_case() -> CorrectAcademicRecord:
    return get_container().correct_academic_record()


def get_student_academic_record_repository():
    return get_container()._student_academic_record_repository()


def get_list_students_use_case() -> ListStudents:
    return get_container().list_students()


def get_get_student_use_case() -> GetStudent:
    return get_container().get_student()


def get_list_student_academic_periods_use_case() -> ListStudentAcademicPeriods:
    return get_container().list_student_academic_periods()


def get_list_subjects_use_case() -> ListSubjects:
    return get_container().list_subjects()


def get_create_subject_use_case() -> CreateSubject:
    return get_container().create_subject()


def get_update_subject_use_case() -> UpdateSubject:
    return get_container().update_subject()


def get_list_academic_periods_use_case() -> ListAcademicPeriods:
    return get_container().list_academic_periods()


def get_create_academic_period_use_case() -> CreateAcademicPeriod:
    return get_container().create_academic_period()


def get_list_eligible_student_periods_use_case() -> ListEligibleStudentPeriods:
    return get_container().list_eligible_student_periods()


def get_list_eligible_student_subjects_use_case() -> ListEligibleStudentSubjects:
    return get_container().list_eligible_student_subjects()


def get_list_academic_classes_use_case() -> ListAcademicClasses:
    return get_container().list_academic_classes()


def get_create_academic_year_use_case() -> CreateAcademicYear:
    return get_container().create_academic_year()


def get_list_academic_years_use_case() -> ListAcademicYears:
    return get_container().list_academic_years()


def get_change_academic_year_status_use_case() -> ChangeAcademicYearStatus:
    return get_container().change_academic_year_status()


def get_create_student_assignment_use_case() -> CreateStudentAssignment:
    return get_container().create_student_assignment()


def get_list_student_assignments_use_case() -> ListStudentAssignments:
    return get_container().list_student_assignments()


def get_change_student_assignment_status_use_case() -> ChangeStudentAssignmentStatus:
    return get_container().change_student_assignment_status()


def get_record_attendance_use_case() -> RecordAttendance:
    return get_container().record_attendance()


def get_list_class_attendance_use_case() -> ListClassAttendance:
    return get_container().list_class_attendance()


def get_get_attendance_statistics_use_case() -> GetAttendanceStatistics:
    return get_container().get_attendance_statistics()


def get_correct_attendance_use_case() -> CorrectAttendance:
    return get_container().correct_attendance()


def get_analyze_student_academic_risk_use_case() -> AnalyzeStudentAcademicRisk:
    return get_container().analyze_student_academic_risk()


def get_list_student_attendance_use_case() -> ListStudentAttendance:
    return get_container().list_student_attendance()


def get_prepare_deliberation_use_case() -> PrepareDeliberation:
    return get_container().prepare_deliberation()


def get_apply_student_promotion_use_case() -> ApplyStudentPromotion:
    return get_container().apply_student_promotion()


def get_validate_deliberation_use_case() -> ValidateDeliberation:
    return get_container().validate_deliberation()


def get_prepare_report_card_use_case() -> PrepareReportCard:
    return get_container().prepare_report_card()


def get_publish_report_card_use_case() -> PublishReportCard:
    return get_container().publish_report_card()


def get_list_student_report_cards_use_case() -> ListStudentReportCards:
    return get_container().list_student_report_cards()


def get_student_report_card_use_case() -> GetStudentReportCard:
    return get_container().get_student_report_card()


def get_correct_report_card_use_case() -> CorrectReportCard:
    return get_container().correct_report_card()


def get_report_card_renderer() -> ReportCardRenderer:
    return PdfReportCardRenderer()


def get_assign_subject_to_class_use_case() -> AssignSubjectToClass:
    return get_container().assign_subject_to_class()


def get_analyze_academic_risk_use_case() -> AnalyzeAcademicRisk:
    return get_container().analyze_academic_risk()


def get_enable_two_factor_use_case() -> EnableTwoFactor:
    return get_container().enable_two_factor()


def get_login_user_use_case() -> LoginUser:
    return get_container().login_user()


def get_login_with_google_use_case() -> LoginWithGoogle:
    return get_container().login_with_google()


def get_link_google_identity_use_case() -> LinkGoogleIdentity:
    return get_container().link_google_identity()


def get_refresh_access_token_use_case() -> RefreshAccessToken:
    return get_container().refresh_access_token()


def get_register_user_use_case() -> RegisterUser:
    return get_container().register_user()


def get_verify_login_two_factor_use_case() -> VerifyLoginTwoFactor:
    return get_container().verify_login_two_factor()


def get_verify_two_factor_use_case() -> VerifyTwoFactor:
    return get_container().verify_two_factor()
