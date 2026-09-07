import os
from dataclasses import dataclass, field


DEVELOPMENT_ENVIRONMENTS = frozenset({"development", "test"})

ALLOWED_ENVIRONMENTS = frozenset(
    {"development", "test", "staging", "production"}
)

DEVELOPMENT_JWT_SECRET = (
    "edunova-development-secret-key-"
    "32-bytes-minimum-change-in-production"
)

MINIMUM_JWT_SECRET_LENGTH = 32

FORBIDDEN_JWT_SECRETS = frozenset(
    {
        DEVELOPMENT_JWT_SECRET,
        "change-this-secret-in-production",
        "secret",
        "changeme",
    }
)


@dataclass(frozen=True)
class Settings:
    environment: str
    jwt_secret: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    database_path: str
    cors_allowed_origins: tuple[str, ...] = field(default=())
    docs_enabled: bool = True
    auth_rate_limit_attempts: int = 10
    auth_rate_limit_window_seconds: int = 60

    @property
    def is_production(self) -> bool:
        return self.environment not in DEVELOPMENT_ENVIRONMENTS

    @classmethod
    def from_environment(cls) -> "Settings":
        environment = os.getenv(
            "EDUNOVA_ENVIRONMENT",
            "development",
        ).strip().lower()

        if environment not in ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "EDUNOVA_ENVIRONMENT doit valoir "
                "development, test, staging ou production."
            )

        is_production = environment not in DEVELOPMENT_ENVIRONMENTS

        jwt_secret = os.getenv(
            "EDUNOVA_JWT_SECRET",
            "",
        ).strip()

        # En développement et en test uniquement, nous conservons
        # une valeur par défaut non destinée à la production.
        if not jwt_secret:
            if is_production:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET doit etre defini "
                    "en environnement de production."
                )

            jwt_secret = DEVELOPMENT_JWT_SECRET

        if is_production:
            if jwt_secret in FORBIDDEN_JWT_SECRETS:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET ne peut pas reutiliser "
                    "une valeur par defaut connue."
                )

            if len(jwt_secret) < MINIMUM_JWT_SECRET_LENGTH:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET doit contenir au moins "
                    f"{MINIMUM_JWT_SECRET_LENGTH} caracteres."
                )

        access_token_expire_minutes = _read_positive_int(
            "EDUNOVA_ACCESS_TOKEN_EXPIRE_MINUTES",
            "15",
            "La duree du token access doit etre positive.",
        )

        refresh_token_expire_days = _read_positive_int(
            "EDUNOVA_REFRESH_TOKEN_EXPIRE_DAYS",
            "7",
            "La duree du token refresh doit etre positive.",
        )

        database_path = os.getenv(
            "EDUNOVA_DATABASE_PATH",
            "edunova.db",
        )

        if not database_path.strip():
            raise ValueError(
                "Le chemin de la base de donnees ne peut pas etre vide."
            )

        cors_allowed_origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "EDUNOVA_CORS_ALLOWED_ORIGINS",
                "",
            ).split(",")
            if origin.strip()
        )

        if "*" in cors_allowed_origins and is_production:
            raise ValueError(
                "EDUNOVA_CORS_ALLOWED_ORIGINS ne peut pas etre "
                "un joker en production."
            )

        docs_enabled = _read_bool(
            "EDUNOVA_DOCS_ENABLED",
            default=not is_production,
        )

        auth_rate_limit_attempts = _read_positive_int(
            "EDUNOVA_AUTH_RATE_LIMIT_ATTEMPTS",
            "10",
            "Le nombre de tentatives autorisees doit etre positif.",
        )

        auth_rate_limit_window_seconds = _read_positive_int(
            "EDUNOVA_AUTH_RATE_LIMIT_WINDOW_SECONDS",
            "60",
            "La fenetre de limitation doit etre positive.",
        )

        return cls(
            environment=environment,
            jwt_secret=jwt_secret,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
            database_path=database_path,
            cors_allowed_origins=cors_allowed_origins,
            docs_enabled=docs_enabled,
            auth_rate_limit_attempts=auth_rate_limit_attempts,
            auth_rate_limit_window_seconds=(
                auth_rate_limit_window_seconds
            ),
        )


def _read_positive_int(
    variable: str,
    default: str,
    error_message: str,
) -> int:
    raw_value = os.getenv(variable, default)

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(error_message) from exc

    if value <= 0:
        raise ValueError(error_message)

    return value


def _read_bool(variable: str, default: bool) -> bool:
    raw_value = os.getenv(variable)

    if raw_value is None or not raw_value.strip():
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "on"}
