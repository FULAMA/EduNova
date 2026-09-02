import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str
    jwt_secret: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    database_path: str
    cors_allowed_origins: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> "Settings":
        environment = os.getenv(
            "EDUNOVA_ENVIRONMENT",
            "development",
        ).strip().lower()

        jwt_secret = os.getenv(
            "EDUNOVA_JWT_SECRET",
            "",
        ).strip()

        if not jwt_secret:
            if environment in {"development", "test"}:
                jwt_secret = (
                    "edunova-development-secret-key-"
                    "32-bytes-minimum-change-in-production"
                )
            else:
                raise ValueError(
                    "EDUNOVA_JWT_SECRET doit etre defini "
                    "en environnement de production."
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

        if environment == "production" and "*" in cors_allowed_origins:
            raise ValueError(
                "L origine CORS '*' est interdite en production."
            )

        return cls(
            environment=environment,
            jwt_secret=jwt_secret,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
            database_path=database_path,
            cors_allowed_origins=cors_allowed_origins,
        )
