from pathlib import Path

from src.infrastructure.security.jwt_service import JwtService
from src.infrastructure.security.google_identity_verifier import (
    GoogleIdTokenVerifier,
)
from src.identity.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from src.identity.infrastructure.security.pyotp_two_factor_service import (
    PyOtpTwoFactorService,
)

from src.academic.application.use_cases.add_subject_result import AddSubjectResult
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
from src.infrastructure.repositories.sqlite_deliberation_repository import SQLiteDeliberationRepository
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
from src.academic.application.use_cases.change_student_assignment_status import ChangeStudentAssignmentStatus
from src.identity.application.use_cases.link_student_account import LinkStudentAccount
from src.identity.application.use_cases.get_student_portal_profile import GetStudentPortalProfile
from src.infrastructure.repositories.sqlite_academic_period_repository import SQLiteAcademicPeriodRepository
from src.infrastructure.repositories.sqlite_student_user_link_repository import SQLiteStudentUserLinkRepository
from src.infrastructure.repositories.sqlite_attendance_repository import SQLiteAttendanceRepository
from src.infrastructure.repositories.sqlite_report_card_repository import SQLiteReportCardRepository
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

from src.academic.domain.services.academic_risk_analyzer import AcademicRiskAnalyzer

from src.infrastructure.config.settings import Settings
from src.infrastructure.bootstrap.development_seed import seed_development_data
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_academic_class_repository import (
    SQLiteAcademicClassRepository,
)
from src.infrastructure.repositories.sqlite_academic_year_repository import SQLiteAcademicYearRepository
from src.infrastructure.repositories.sqlite_student_assignment_repository import SQLiteStudentAssignmentRepository
from src.infrastructure.repositories.sqlite_academic_option_repository import (
    SQLiteAcademicOptionRepository,
)
from src.infrastructure.repositories.sqlite_class_option_repository import (
    SQLiteClassOptionRepository,
)
from src.infrastructure.repositories.sqlite_class_subject_repository import (
    SQLiteClassSubjectRepository,
)
from src.infrastructure.repositories.sqlite_refresh_token_repository import (
    SQLiteRefreshTokenRepository,
)
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)
from src.infrastructure.repositories.sqlite_student_repository import (
    SQLiteStudentRepository,
)
from src.infrastructure.repositories.sqlite_external_identity_repository import (
    SQLiteExternalIdentityRepository,
)
from src.infrastructure.repositories.sqlite_subject_repository import (
    SQLiteSubjectRepository,
)
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.shared.application.events.in_memory_event_dispatcher import (
    InMemoryEventDispatcher,
)
from src.tenancy.infrastructure.repositories.sqlite_membership_repository import SQLiteMembershipRepository
from src.billing.application.service import BillingService
from src.infrastructure.repositories.sqlite_billing_repository import SQLiteBillingRepository
from src.tenancy.infrastructure.repositories.sqlite_tenant_repository import SQLiteTenantRepository


class ApplicationContainer:

    def __init__(
        self,
        database: SQLiteDatabase | None = None,
        database_path: str | Path = "edunova.db",
        settings: Settings | None = None,
    ):
        self._settings = settings or Settings.from_environment()

        self._database = database or SQLiteDatabase(
            settings.database_path if settings is not None else database_path
        )
        self._database.initialize()

        if self._settings.development_seed_enabled:
            password = self._settings.development_seed_password
            if password is None:
                raise ValueError(
                    "EDUNOVA_DEV_SEED_PASSWORD doit etre defini si le seed est active."
                )
            seed_development_data(
                self._database,
                password,
                self._settings.development_seed_email,
            )

        self._refresh_token_repository_instance = (
            SQLiteRefreshTokenRepository(self._database)
        )

        # No SubjectResultAdded business consumer is registered at present.
        self._event_dispatcher = InMemoryEventDispatcher()

    def _jwt_service(self) -> JwtService:
        return JwtService(
            secret_key=self._settings.jwt_secret,
            access_token_expire_minutes=(
                self._settings.access_token_expire_minutes
            ),
            refresh_token_expire_days=(
                self._settings.refresh_token_expire_days
            ),
        )

    def _student_academic_record_repository(
        self,
    ) -> SQLiteStudentAcademicRecordRepository:
        return SQLiteStudentAcademicRecordRepository(
            self._database
        )

    def _student_repository(self) -> SQLiteStudentRepository:
        return SQLiteStudentRepository(self._database)

    def _academic_class_repository(
        self,
    ) -> SQLiteAcademicClassRepository:
        return SQLiteAcademicClassRepository(
            self._database
        )

    def _academic_option_repository(
        self,
    ) -> SQLiteAcademicOptionRepository:
        return SQLiteAcademicOptionRepository(
            self._database
        )

    def _subject_repository(
        self,
    ) -> SQLiteSubjectRepository:
        return SQLiteSubjectRepository(
            self._database
        )

    def _academic_period_repository(self) -> SQLiteAcademicPeriodRepository:
        return SQLiteAcademicPeriodRepository(self._database)

    def _attendance_repository(self) -> SQLiteAttendanceRepository:
        return SQLiteAttendanceRepository(self._database)

    def billing_service(self) -> BillingService:
        return BillingService(SQLiteBillingRepository(self._database))

    def record_attendance(self) -> RecordAttendance:
        return RecordAttendance(self._attendance_repository(), self._student_repository(),
            self._academic_year_repository(), self._academic_period_repository())

    def list_class_attendance(self) -> ListClassAttendance:
        return ListClassAttendance(self._attendance_repository(), self._academic_period_repository())

    def get_attendance_statistics(self) -> GetAttendanceStatistics:
        return GetAttendanceStatistics(self._attendance_repository())

    def correct_attendance(self) -> CorrectAttendance:
        return CorrectAttendance(self._attendance_repository())

    def analyze_student_academic_risk(self) -> AnalyzeStudentAcademicRisk:
        return AnalyzeStudentAcademicRisk(
            self._student_academic_record_repository(), self._attendance_repository()
        )

    def list_student_attendance(self) -> ListStudentAttendance:
        return ListStudentAttendance(self._attendance_repository())

    def prepare_deliberation(self) -> PrepareDeliberation:
        return PrepareDeliberation(self._student_academic_record_repository(), deliberations=SQLiteDeliberationRepository(self._database))

    def apply_student_promotion(self) -> ApplyStudentPromotion:
        return ApplyStudentPromotion(
            self._student_assignment_repository(),
            SQLiteDeliberationRepository(self._database),
            self._academic_year_repository(),
            self._academic_class_repository(),
            self._student_academic_record_repository(),
        )

    def validate_deliberation(self) -> ValidateDeliberation:
        return ValidateDeliberation(
            SQLiteDeliberationRepository(self._database),
            self._student_academic_record_repository(),
        )

    def _report_card_repository(self) -> SQLiteReportCardRepository:
        return SQLiteReportCardRepository(self._database)

    def prepare_report_card(self) -> PrepareReportCard:
        return PrepareReportCard(
            self._student_academic_record_repository(),
            SQLiteDeliberationRepository(self._database),
            self._report_card_repository(),
        )

    def publish_report_card(self) -> PublishReportCard:
        return PublishReportCard(
            self._report_card_repository(),
            SQLiteDeliberationRepository(self._database),
            self._student_academic_record_repository(),
        )

    def list_student_report_cards(self) -> ListStudentReportCards:
        return ListStudentReportCards(self._report_card_repository())

    def get_student_report_card(self) -> GetStudentReportCard:
        return GetStudentReportCard(self._report_card_repository())

    def correct_report_card(self) -> CorrectReportCard:
        return CorrectReportCard(
            self._report_card_repository(), self.prepare_report_card()
        )

    def _academic_year_repository(self) -> SQLiteAcademicYearRepository:
        return SQLiteAcademicYearRepository(self._database)

    def _student_assignment_repository(self) -> SQLiteStudentAssignmentRepository:
        return SQLiteStudentAssignmentRepository(self._database)

    def _class_option_repository(
        self,
    ) -> SQLiteClassOptionRepository:
        return SQLiteClassOptionRepository(
            self._database
        )

    def _class_subject_repository(
        self,
    ) -> SQLiteClassSubjectRepository:
        return SQLiteClassSubjectRepository(
            self._database
        )

    def _user_repository(
        self,
    ) -> SQLiteUserRepository:
        return SQLiteUserRepository(
            self._database
        )

    def _external_identity_repository(
        self,
    ) -> SQLiteExternalIdentityRepository:
        return SQLiteExternalIdentityRepository(self._database)

    def _refresh_token_repository(
        self,
    ) -> SQLiteRefreshTokenRepository:
        return self._refresh_token_repository_instance

    def _membership_repository(self) -> SQLiteMembershipRepository:
        return SQLiteMembershipRepository(self._database)

    def _student_user_link_repository(self) -> SQLiteStudentUserLinkRepository:
        return SQLiteStudentUserLinkRepository(self._database)

    def link_student_account(self) -> LinkStudentAccount:
        return LinkStudentAccount(
            links=self._student_user_link_repository(),
            students=self._student_repository(),
            users=self._user_repository(),
            memberships=self._membership_repository(),
        )

    def get_student_portal_profile(self) -> GetStudentPortalProfile:
        return GetStudentPortalProfile(
            self._student_user_link_repository(),
            self._student_repository(),
            self._student_assignment_repository(),
            self._academic_year_repository(),
        )

    def _tenant_repository(self) -> SQLiteTenantRepository:
        return SQLiteTenantRepository(self._database)

    def analyze_student_academic_record(
        self,
    ) -> AnalyzeStudentAcademicRecord:
        return AnalyzeStudentAcademicRecord(
            self._student_academic_record_repository(), self._subject_repository(),
            self._academic_period_repository(),
        )

    def list_subjects(self) -> ListSubjects:
        return ListSubjects(self._subject_repository())

    def create_subject(self) -> CreateSubject:
        return CreateSubject(self._subject_repository())

    def update_subject(self) -> UpdateSubject:
        return UpdateSubject(self._subject_repository())

    def list_academic_periods(self) -> ListAcademicPeriods:
        return ListAcademicPeriods(self._academic_period_repository())

    def create_academic_period(self) -> CreateAcademicPeriod:
        return CreateAcademicPeriod(self._academic_period_repository(), self._academic_year_repository())

    def list_eligible_student_periods(self) -> ListEligibleStudentPeriods:
        return ListEligibleStudentPeriods(
            self._student_assignment_repository(), self._academic_period_repository(),
            self._student_academic_record_repository(), self._academic_year_repository(),
        )

    def list_eligible_student_subjects(self) -> ListEligibleStudentSubjects:
        return ListEligibleStudentSubjects(
            self._student_assignment_repository(), self._academic_period_repository(),
            self._class_subject_repository(), self._subject_repository(),
        )

    def list_academic_classes(self) -> ListAcademicClasses:
        return ListAcademicClasses(self._academic_class_repository())

    def create_academic_year(self) -> CreateAcademicYear:
        return CreateAcademicYear(self._academic_year_repository())

    def list_academic_years(self) -> ListAcademicYears:
        return ListAcademicYears(self._academic_year_repository())

    def change_academic_year_status(self) -> ChangeAcademicYearStatus:
        return ChangeAcademicYearStatus(self._academic_year_repository())

    def create_student_assignment(self) -> CreateStudentAssignment:
        return CreateStudentAssignment(
            assignment_repository=self._student_assignment_repository(),
            student_repository=self._student_repository(),
            class_repository=self._academic_class_repository(),
            year_repository=self._academic_year_repository(),
            option_repository=self._academic_option_repository(),
            class_option_repository=self._class_option_repository(),
        )

    def list_student_assignments(self) -> ListStudentAssignments:
        return ListStudentAssignments(self._student_assignment_repository())

    def change_student_assignment_status(self) -> ChangeStudentAssignmentStatus:
        return ChangeStudentAssignmentStatus(
            assignments=self._student_assignment_repository(),
            years=self._academic_year_repository(),
        )

    def add_subject_result(
        self,
    ) -> AddSubjectResult:
        return AddSubjectResult(
            self._student_academic_record_repository(),
            self._event_dispatcher,
            assignments=self._student_assignment_repository(),
            periods=self._academic_period_repository(),
            class_subjects=self._class_subject_repository(),
            subjects=self._subject_repository(),
        )

    def create_academic_record(
        self,
    ) -> CreateAcademicRecord:
        return CreateAcademicRecord(
            self._student_academic_record_repository(),
            assignments=self._student_assignment_repository(),
            periods=self._academic_period_repository(),
        )

    def validate_academic_record(self) -> ValidateAcademicRecord:
        return ValidateAcademicRecord(self._student_academic_record_repository())

    def correct_academic_record(self) -> CorrectAcademicRecord:
        return CorrectAcademicRecord(self._student_academic_record_repository())

    def list_students(self) -> ListStudents:
        return ListStudents(self._student_repository())

    def get_student(self) -> GetStudent:
        return GetStudent(self._student_repository())

    def list_student_academic_periods(self) -> ListStudentAcademicPeriods:
        return ListStudentAcademicPeriods(
            self._student_academic_record_repository(), self._academic_period_repository()
        )

    def assign_subject_to_class(
        self,
    ) -> AssignSubjectToClass:
        return AssignSubjectToClass(
            academic_class_repository=self._academic_class_repository(),
            subject_repository=self._subject_repository(),
            class_subject_repository=self._class_subject_repository(),
            class_option_repository=self._class_option_repository(),
        )

    def analyze_academic_risk(
        self,
    ) -> AnalyzeAcademicRisk:
        return AnalyzeAcademicRisk(
            AcademicRiskAnalyzer()
        )

    def enable_two_factor(
        self,
    ) -> EnableTwoFactor:
        return EnableTwoFactor(
            user_repository=self._user_repository(),
            membership_repository=self._membership_repository(),
            two_factor_service=PyOtpTwoFactorService(),
        )

    def verify_two_factor(
        self,
    ) -> VerifyTwoFactor:
        return VerifyTwoFactor(
            user_repository=self._user_repository(),
            membership_repository=self._membership_repository(),
            two_factor_service=PyOtpTwoFactorService(),
        )

    def register_user(
        self,
    ) -> RegisterUser:
        return RegisterUser(
            user_repository=self._user_repository(),
            password_hasher=Argon2PasswordHasher(),
        )

    def login_user(
        self,
    ) -> LoginUser:
        return LoginUser(
            user_repository=self._user_repository(),
            membership_repository=self._membership_repository(),
            tenant_repository=self._tenant_repository(),
            password_hasher=Argon2PasswordHasher(),
            two_factor_service=PyOtpTwoFactorService(),
            jwt_service=self._jwt_service(),
        )

    def login_with_google(self) -> LoginWithGoogle:
        return LoginWithGoogle(
            user_repository=self._user_repository(),
            membership_repository=self._membership_repository(),
            tenant_repository=self._tenant_repository(),
            external_identity_repository=self._external_identity_repository(),
            google_identity_verifier=GoogleIdTokenVerifier(
                self._settings.google_client_id,
            ),
            jwt_service=self._jwt_service(),
        )

    def link_google_identity(self) -> LinkGoogleIdentity:
        return LinkGoogleIdentity(
            user_repository=self._user_repository(),
            external_identity_repository=self._external_identity_repository(),
            google_identity_verifier=GoogleIdTokenVerifier(
                self._settings.google_client_id,
            ),
        )

    def verify_login_two_factor(
        self,
    ) -> VerifyLoginTwoFactor:
        return VerifyLoginTwoFactor(
            user_repository=self._user_repository(),
            membership_repository=self._membership_repository(),
            tenant_repository=self._tenant_repository(),
            two_factor_service=PyOtpTwoFactorService(),
            jwt_service=self._jwt_service(),
        )

    def refresh_access_token(
        self,
    ) -> RefreshAccessToken:
        return RefreshAccessToken(
            user_repository=self._user_repository(),
            membership_repository=self._membership_repository(),
            tenant_repository=self._tenant_repository(),
            refresh_token_repository=self._refresh_token_repository(),
            jwt_service=self._jwt_service(),
        )
