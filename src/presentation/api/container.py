from pathlib import Path

from src.infrastructure.security.jwt_service import JwtService
from src.identity.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from src.identity.infrastructure.security.pyotp_two_factor_service import (
    PyOtpTwoFactorService,
)

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

from src.academic.domain.services.academic_risk_analyzer import AcademicRiskAnalyzer

from src.infrastructure.config.settings import Settings
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_academic_class_repository import (
    SQLiteAcademicClassRepository,
)
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
from src.infrastructure.repositories.sqlite_subject_repository import (
    SQLiteSubjectRepository,
)
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.tenancy.infrastructure.repositories.sqlite_membership_repository import SQLiteMembershipRepository
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

        self._refresh_token_repository_instance = (
            SQLiteRefreshTokenRepository(self._database)
        )

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

    def _refresh_token_repository(
        self,
    ) -> SQLiteRefreshTokenRepository:
        return self._refresh_token_repository_instance

    def _membership_repository(self) -> SQLiteMembershipRepository:
        return SQLiteMembershipRepository(self._database)

    def _tenant_repository(self) -> SQLiteTenantRepository:
        return SQLiteTenantRepository(self._database)

    def analyze_student_academic_record(
        self,
    ) -> AnalyzeStudentAcademicRecord:
        return AnalyzeStudentAcademicRecord(
            self._student_academic_record_repository()
        )

    def add_subject_result(
        self,
    ) -> AddSubjectResult:
        return AddSubjectResult(
            self._student_academic_record_repository()
        )

    def create_academic_record(
        self,
    ) -> CreateAcademicRecord:
        return CreateAcademicRecord(
            self._student_academic_record_repository()
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
