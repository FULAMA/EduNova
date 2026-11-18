import sqlite3
import unicodedata
from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import (
    StudentRepository,
)
from src.academic.domain.entities.student import Student
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteStudentRepository(StudentRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def list_by_tenant(self, tenant_id: UUID) -> tuple[StudentSummary, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, first_name, last_name, email, active, registration_number
                FROM students
                WHERE tenant_id = ?
                ORDER BY last_name, first_name, id
                """,
                (str(tenant_id),),
            ).fetchall()

        return tuple(
            StudentSummary(
                id=UUID(row["id"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                active=bool(row["active"]),
                registration_number=row["registration_number"],
            )
            for row in rows
        )

    def get_by_id_and_tenant(
        self,
        student_id: UUID,
        tenant_id: UUID,
    ) -> StudentSummary | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, first_name, last_name, email, active, registration_number
                FROM students
                WHERE id = ? AND tenant_id = ?
                """,
                (str(student_id), str(tenant_id)),
            ).fetchone()

        if row is None:
            return None

        return StudentSummary(
            id=UUID(row["id"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            active=bool(row["active"]),
            registration_number=row["registration_number"],
        )

    def find_by_registration_number(
        self,
        tenant_id: UUID,
        registration_number: str,
    ) -> StudentSummary | None:
        clean_reg = registration_number.strip()
        if not clean_reg:
            return None
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, first_name, last_name, email, active, registration_number
                FROM students
                WHERE tenant_id = ? AND registration_number = ?
                """,
                (str(tenant_id), clean_reg),
            ).fetchone()
        if row is None:
            return None
        return StudentSummary(
            id=UUID(row["id"]),
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            active=bool(row["active"]),
            registration_number=row["registration_number"],
        )

    def find_potential_duplicates(
        self,
        tenant_id: UUID,
        first_name: str,
        last_name: str,
        exclude_id: UUID | None = None,
    ) -> tuple[StudentSummary, ...]:
        def normalize(value: str) -> str:
            return " ".join(unicodedata.normalize("NFKC", value).casefold().split())

        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, first_name, last_name, email, active, registration_number
                FROM students
                WHERE tenant_id = ?
                """,
                (str(tenant_id),),
            ).fetchall()

        normalized_first = normalize(first_name)
        normalized_last = normalize(last_name)
        return tuple(
            StudentSummary(
                id=UUID(row["id"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                active=bool(row["active"]),
                registration_number=row["registration_number"],
            )
            for row in rows
            if UUID(row["id"]) != exclude_id
            and normalize(row["first_name"]) == normalized_first
            and normalize(row["last_name"]) == normalized_last
        )

    def save(self, student: Student) -> None:
        with self._database.connect() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO students (
                        id, tenant_id, first_name, last_name, email, phone, registration_number, active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(student.id),
                        str(student.tenant_id),
                        student.first_name,
                        student.last_name,
                        student.email,
                        student.phone,
                        student.registration_number,
                        int(student.active),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                if "registration_number" in str(exc).lower() or "uq_students_tenant_registration_number" in str(exc).lower():
                    raise ValueError("Le matricule scolaire est deja attribue dans cet etablissement.") from exc
                raise

    def update(self, student: Student) -> None:
        with self._database.connect() as connection:
            try:
                cursor = connection.execute(
                    """
                    UPDATE students
                    SET first_name = ?, last_name = ?, email = ?, phone = ?, registration_number = ?, active = ?
                    WHERE id = ? AND tenant_id = ?
                    """,
                    (
                        student.first_name,
                        student.last_name,
                        student.email,
                        student.phone,
                        student.registration_number,
                        int(student.active),
                        str(student.id),
                        str(student.tenant_id),
                    ),
                )
                if cursor.rowcount == 0:
                    raise LookupError("Eleve introuvable.")
            except sqlite3.IntegrityError as exc:
                if "registration_number" in str(exc).lower() or "uq_students_tenant_registration_number" in str(exc).lower():
                    raise ValueError("Le matricule scolaire est deja attribue dans cet etablissement.") from exc
                raise
