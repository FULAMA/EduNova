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
            if len(jwt_secret) < _MINIMUM_JWT_SECRET_LENGTH:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET doit contenir au moins "
                    f"{_MINIMUM_JWT_SECRET_LENGTH} caracteres en staging/production."
                )
            if jwt_secret.lower() in _FORBIDDEN_JWT_SECRETS:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET ne peut pas utiliser une valeur faible ou connue."
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
        )
