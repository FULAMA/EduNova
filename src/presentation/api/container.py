from pathlib import Path

from src.application.services.jwt_service import JwtService
from src.application.services.password_hasher_service import (
    PasswordHasherService,
)
from src.application.services.two_factor_service import (
    TwoFactorService,
)

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

from src.domain.services.academic_risk_analyzer import AcademicRiskAnalyzer

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
from src.presentation.api.security.rate_limiter import RateLimiter


class ApplicationContainer:

    def __init__(
        self,
        database: SQLiteDatabase | None = None,
        database_path: str | Path = "edunova.db",
        settings: Settings | None = None,
    ):
        self._settings = settings or Settings.from_environment()

        self._database = database or SQLiteDatabase(database_path)
        self._database.initialize()

        self._refresh_token_repository_instance = (
            SQLiteRefreshTokenRepository(self._database)
        )

        self._auth_rate_limiter = RateLimiter(
            max_attempts=self._settings.auth_rate_limit_attempts,
            window_seconds=(
                self._settings.auth_rate_limit_window_seconds
            ),
        )

    @property
    def settings(self) -> Settings:
        return self._settings

    def auth_rate_limiter(self) -> RateLimiter:
        return self._auth_rate_limiter

    def jwt_service(self) -> JwtService:
        return self._jwt_service()

    def user_repository(self) -> SQLiteUserRepository:
        return self._user_repository()

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
            two_factor_service=TwoFactorService(),
        )

    def verify_two_factor(
        self,
    ) -> VerifyTwoFactor:
        return VerifyTwoFactor(
            user_repository=self._user_repository(),
            two_factor_service=TwoFactorService(),
        )

    def register_user(
        self,
    ) -> RegisterUser:
        return RegisterUser(
            user_repository=self._user_repository(),
            password_hasher=PasswordHasherService(),
        )

    def login_user(
        self,
    ) -> LoginUser:
        return LoginUser(
            user_repository=self._user_repository(),
            password_hasher=PasswordHasherService(),
            two_factor_service=TwoFactorService(),
            jwt_service=self._jwt_service(),
        )

    def verify_login_two_factor(
        self,
    ) -> VerifyLoginTwoFactor:
        return VerifyLoginTwoFactor(
            user_repository=self._user_repository(),
            two_factor_service=TwoFactorService(),
            jwt_service=self._jwt_service(),
        )

    def refresh_access_token(
        self,
    ) -> RefreshAccessToken:
        return RefreshAccessToken(
            user_repository=self._user_repository(),
            refresh_token_repository=self._refresh_token_repository(),
            jwt_service=self._jwt_service(),
        )
