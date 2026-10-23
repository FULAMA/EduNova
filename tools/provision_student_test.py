"""Provision a disposable student account for local portal testing.

This script is intentionally not exposed through FastAPI. It only accepts a
new SQLite database below a dedicated system temporary directory.
"""

from __future__ import annotations

import argparse
import getpass
import secrets
import tempfile
from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

from src.academic.domain.entities.academic_class import AcademicClass
from src.identity.application.dto.register_user_request import RegisterUserRequest
from src.infrastructure.config.settings import Settings
from src.presentation.api.container import ApplicationContainer
from src.tenancy.domain.entities.membership import Membership


PROTECTED_DATABASES = {"edunova.db", "edunova_dev.db"}
DEFAULT_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


def _safe_database_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser().resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()

    if path.name.lower() in PROTECTED_DATABASES:
        raise ValueError("Les bases permanentes EduNova sont interdites.")
    if path.suffix.lower() != ".db":
        raise ValueError("Le chemin doit désigner un fichier SQLite .db.")
    try:
        path.relative_to(temp_root)
    except ValueError as exc:
        raise ValueError("La base doit être située sous le dossier temporaire système.") from exc
    if not path.parent.name.startswith("edunova-student-"):
        raise ValueError(
            "Le dossier parent doit commencer par 'edunova-student-'."
        )
    if path.exists():
        raise ValueError("La base temporaire doit être nouvelle et inexistante.")

    path.parent.mkdir(parents=True, exist_ok=False)
    return path


def _create_tenant_and_student(container: ApplicationContainer, tenant_id: UUID) -> UUID:
    student_id = uuid4()
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO tenants (id, name, slug, active) VALUES (?, ?, ?, 1)",
            (str(tenant_id), "EduNova Student Test", f"student-test-{tenant_id}"),
        )
        connection.execute(
            """
            INSERT INTO students (id, tenant_id, first_name, last_name, email, phone, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                str(student_id),
                str(tenant_id),
                "Eleve",
                "Synthétique",
                None,
                None,
            ),
        )
    return student_id


def provision(database: str, email: str, password: str) -> dict[str, str]:
    database_path = _safe_database_path(database)
    tenant_id = DEFAULT_TENANT_ID
    settings = Settings(
        environment="development",
        jwt_secret=secrets.token_urlsafe(32),
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
        database_path=str(database_path),
        cors_allowed_origins=("http://127.0.0.1:5173",),
        development_seed_enabled=False,
    )
    container = ApplicationContainer(settings=settings)

    admin = container.register_user().execute(
        RegisterUserRequest(
            email=f"admin-{uuid4()}@student-test.invalid",
            password=secrets.token_urlsafe(24),
            role="ADMIN",
        )
    )
    student = container.register_user().execute(
        RegisterUserRequest(email=email, password=password, role="STUDENT")
    )
    student_id = _create_tenant_and_student(container, tenant_id)
    container._membership_repository().save(
        Membership(uuid4(), admin.id, tenant_id, "ADMIN")
    )
    container._membership_repository().save(
        Membership(uuid4(), student.id, tenant_id, "STUDENT")
    )

    academic_class = AcademicClass(uuid4(), tenant_id, "Classe test")
    container._academic_class_repository().save(academic_class)
    year = container.create_academic_year().execute(
        tenant_id, "2026-2027", date(2026, 9, 1), date(2027, 7, 31)
    )
    container.change_academic_year_status().activate(year.id, tenant_id)
    assignment = container.create_student_assignment().execute(
        tenant_id=tenant_id,
        student_id=student_id,
        academic_year_id=year.id,
        academic_class_id=academic_class.id,
        created_by=admin.id,
    )
    container.change_student_assignment_status().activate(assignment.id, tenant_id)
    container.link_student_account().execute(
        tenant_id, student.id, student_id, admin.id
    )

    return {
        "database": str(database_path),
        "tenant_id": str(tenant_id),
        "student_id": str(student_id),
        "student_user_id": str(student.id),
        "student_email": email,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Mot de passe du compte de test (non affiché): ")
    if not password:
        raise SystemExit("Le mot de passe ne peut pas être vide.")
    for key, value in provision(args.database, args.email, password).items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
