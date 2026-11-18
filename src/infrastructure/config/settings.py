import os
import secrets
from dataclasses import dataclass


_DEVELOPMENT_JWT_SECRET = secrets.token_urlsafe(32)
_ALLOWED_ENVIRONMENTS = frozenset({"development", "test", "staging", "production"})
_PRODUCTION_ENVIRONMENTS = frozenset({"staging", "production"})
_MINIMUM_JWT_SECRET_LENGTH = 32
_FORBIDDEN_JWT_SECRETS = frozenset({
    "secret",
    "changeme",
    "change-me",
    "change-this-secret-in-production",
    "edunova-development-secret",
    "your-secret-key",
    "your-secret-key-here",
})


@dataclass(frozen=True)
class Settings:
    environment: str
    jwt_secret: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    database_path: str
    cors_allowed_origins: tuple[str, ...]
    google_client_id: str | None = None
    development_seed_enabled: bool = False
    development_seed_password: str | None = None
    development_seed_email: str = "admin@edunova.com"
    
    # Integration Settings - External Services
    # Notification Providers
    brevo_api_key: str | None = None
    courier_api_key: str | None = None
    
    # Push Notification Providers
    firebase_credentials_path: str | None = None
    
    # Payment Gateways
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_publishable_key: str | None = None
    flutterwave_secret_key: str | None = None
    flutterwave_public_key: str | None = None
    flutterwave_encryption_key: str | None = None
    
    # Calendar Sync
    google_calendar_enabled: bool = False
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None
    
    # Learning Management Systems
    google_classroom_enabled: bool = False
    moodle_enabled: bool = False
    moodle_base_url: str | None = None
    moodle_token: str | None = None
    
    # Virtual Classrooms
    jitsi_enabled: bool = False
    jitsi_base_url: str | None = None
    
    # Analytics
    posthog_project_id: str | None = None
    posthog_api_key: str | None = None
    posthog_base_url: str | None = None
    
    # Feature Flags
    maintenance_mode: bool = False

    @classmethod
    def from_environment(cls) -> "Settings":
        environment = os.getenv(
            "EDUNOVA_ENVIRONMENT",
            "development",
        ).strip().lower()

        if environment not in _ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "EDUNOVA_ENVIRONMENT doit etre development, test, staging ou production."
            )

        jwt_secret = os.getenv(
            "EDUNOVA_JWT_SECRET",
            "",
        ).strip()

        if not jwt_secret:
            if environment in {"development", "test"}:
                jwt_secret = _DEVELOPMENT_JWT_SECRET
            else:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET doit etre defini "
                    "en environnement staging ou production."
                )

        if environment in _PRODUCTION_ENVIRONMENTS:
            if jwt_secret.lower() in _FORBIDDEN_JWT_SECRETS:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET ne peut pas utiliser une valeur faible ou connue."
                )
            if len(jwt_secret) < _MINIMUM_JWT_SECRET_LENGTH:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET doit contenir au moins "
                    f"{_MINIMUM_JWT_SECRET_LENGTH} caracteres en staging/production."
                )

        access_token_expire_minutes = int(
            os.getenv(
                "EDUNOVA_ACCESS_TOKEN_EXPIRE_MINUTES",
                "15",
            )
        )

        refresh_token_expire_days = int(
            os.getenv(
                "EDUNOVA_REFRESH_TOKEN_EXPIRE_DAYS",
                "7",
            )
        )

        database_path = os.getenv(
            "EDUNOVA_DATABASE_PATH",
            "edunova.db",
        ).strip()

        google_client_id = os.getenv(
            "EDUNOVA_GOOGLE_CLIENT_ID",
            "",
        ).strip() or None

        development_seed_enabled = os.getenv(
            "EDUNOVA_DEV_SEED",
            "false",
        ).strip().lower() in {"1", "true", "yes", "on"}
        development_seed_password = os.getenv(
            "EDUNOVA_DEV_SEED_PASSWORD",
            "",
        ).strip() or None
        development_seed_email = os.getenv(
            "EDUNOVA_DEV_SEED_EMAIL",
            "admin@edunova.com",
        ).strip()

        if development_seed_enabled and environment not in {"development", "test"}:
            raise ValueError(
                "EDUNOVA_DEV_SEED est reserve aux environnements development et test."
            )

        if development_seed_enabled and not development_seed_password:
            raise ValueError(
                "EDUNOVA_DEV_SEED_PASSWORD doit etre defini si le seed est active."
            )

        if development_seed_enabled and not development_seed_email:
            raise ValueError(
                "EDUNOVA_DEV_SEED_EMAIL doit etre defini si le seed est active."
            )

        cors_raw = os.getenv(
            "EDUNOVA_CORS_ALLOWED_ORIGINS",
            "",
        ).strip()

        if cors_raw:
            cors_allowed_origins = tuple(
                origin.strip()
                for origin in cors_raw.split(",")
                if origin.strip()
            )
        elif environment in {"development", "test"}:
            cors_allowed_origins = (
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            )
        else:
            raise ValueError(
                "EDUNOVA_CORS_ALLOWED_ORIGINS doit etre defini "
                "en environnement de production."
            )

        # =====================================================================
        # INTÉGRATIONS EXTERNES
        # =====================================================================

        # --- Notifications ---
        brevo_api_key = os.getenv("BREVO_API_KEY", "").strip() or None
        courier_api_key = os.getenv("COURIER_API_KEY", "").strip() or None
        firebase_credentials_path = (
            os.getenv("FIREBASE_CREDENTIALS_PATH", "").strip() or None
        )

        # --- Paiements ---
        stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip() or None
        stripe_webhook_secret = (
            os.getenv("STRIPE_WEBHOOK_SECRET", "").strip() or None
        )
        stripe_publishable_key = (
            os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip() or None
        )
        flutterwave_secret_key = (
            os.getenv("FLUTTERWAVE_SECRET_KEY", "").strip() or None
        )
        flutterwave_public_key = (
            os.getenv("FLUTTERWAVE_PUBLIC_KEY", "").strip() or None
        )
        flutterwave_encryption_key = (
            os.getenv("FLUTTERWAVE_ENCRYPTION_KEY", "").strip() or None
        )

        # --- Classroom ---
        google_calendar_enabled = os.getenv(
            "GOOGLE_CALENDAR_ENABLED", "false"
        ).strip().lower() in {"true", "1", "yes"}
        google_classroom_enabled = os.getenv(
            "GOOGLE_CLASSROOM_ENABLED", "false"
        ).strip().lower() in {"true", "1", "yes"}
        google_oauth_client_id = (
            os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip() or None
        )
        google_oauth_client_secret = (
            os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "").strip() or None
        )

        # --- LMS ---
        moodle_base_url = os.getenv("MOODLE_BASE_URL", "").strip() or None
        moodle_token = os.getenv("MOODLE_TOKEN", "").strip() or None

        # --- Visio ---
        jitsi_base_url = os.getenv("JITSI_BASE_URL", "").strip() or None

        # --- Analytics ---
        posthog_project_id = os.getenv("POSTHOG_PROJECT_ID", "").strip() or None
        posthog_api_key = os.getenv("POSTHOG_API_KEY", "").strip() or None
        posthog_base_url = os.getenv("POSTHOG_BASE_URL", "").strip() or None

        # --- Feature Flags ---
        maintenance_mode = os.getenv(
            "EDUNOVA_MAINTENANCE_MODE", "false"
        ).strip().lower() in {"true", "1", "yes"}

        if access_token_expire_minutes <= 0:
            raise ValueError(
                "La duree du token access doit etre positive."
            )

        if refresh_token_expire_days <= 0:
            raise ValueError(
                "La duree du token refresh doit etre positive."
            )

        if not database_path:
            raise ValueError(
                "Le chemin de la base de donnees ne peut pas etre vide."
            )

        if not cors_allowed_origins:
            raise ValueError(
                "Au moins une origine CORS doit etre configuree."
            )

        if environment in _PRODUCTION_ENVIRONMENTS and "*" in cors_allowed_origins:
            raise ValueError(
                "L origine CORS '*' est interdite en staging/production."
            )

        return cls(
            environment=environment,
            jwt_secret=jwt_secret,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
            database_path=database_path,
            cors_allowed_origins=cors_allowed_origins,
            google_client_id=google_client_id,
            development_seed_enabled=development_seed_enabled,
            development_seed_password=development_seed_password,
            development_seed_email=development_seed_email,
            # Notifications
            brevo_api_key=brevo_api_key,
            courier_api_key=courier_api_key,
            firebase_credentials_path=firebase_credentials_path,
            # Paiements
            stripe_secret_key=stripe_secret_key,
            stripe_webhook_secret=stripe_webhook_secret,
            stripe_publishable_key=stripe_publishable_key,
            flutterwave_secret_key=flutterwave_secret_key,
            flutterwave_public_key=flutterwave_public_key,
            flutterwave_encryption_key=flutterwave_encryption_key,
            # Classroom
            google_calendar_enabled=google_calendar_enabled,
            google_classroom_enabled=google_classroom_enabled,
            google_oauth_client_id=google_oauth_client_id,
            google_oauth_client_secret=google_oauth_client_secret,
            # LMS
            moodle_base_url=moodle_base_url,
            moodle_token=moodle_token,
            # Visio
            jitsi_base_url=jitsi_base_url,
            # Analytics
            posthog_project_id=posthog_project_id,
            posthog_api_key=posthog_api_key,
            posthog_base_url=posthog_base_url,
            # Feature Flags
            maintenance_mode=maintenance_mode,
        )
