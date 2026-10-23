from uuid import UUID

from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.subject import Subject
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteSubjectRepository(SubjectRepository):

    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def save(self, subject: Subject) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO subjects (
                    id,
                    tenant_id,
                    name,
                    code,
                    coefficient,
                    active
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(subject.id),
                    str(subject.tenant_id),
                    subject.name,
                    subject.code,
                    subject.coefficient,
                    int(subject.active),
                ),
            )

    def update(self, subject: Subject) -> None:
        with self._database.connect() as connection:
            cursor = connection.execute(
                """UPDATE subjects SET name = ?, code = ?, coefficient = ?, active = ?
                WHERE id = ? AND tenant_id = ?""",
                (subject.name, subject.code, subject.coefficient, int(subject.active),
                 str(subject.id), str(subject.tenant_id)),
            )
            if cursor.rowcount != 1:
                raise LookupError("Matière introuvable.")

    def list_by_tenant(self, tenant_id: UUID, search: str | None = None) -> list[Subject]:
        query = """SELECT id, tenant_id, name, code, coefficient, active
            FROM subjects WHERE tenant_id = ?"""
        params: list[object] = [str(tenant_id)]
        if search:
            query += " AND name LIKE ? COLLATE NOCASE"
            params.append(f"%{search.strip()}%")
        query += " ORDER BY name COLLATE NOCASE, id"
        with self._database.connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [Subject(UUID(row["id"]), UUID(row["tenant_id"]), row["name"],
                        row["code"], row["coefficient"], bool(row["active"]))
                for row in rows]

    def find_many_by_ids(self, subject_ids: set[UUID], tenant_id: UUID) -> dict[UUID, Subject]:
        if not subject_ids:
            return {}
        return {
            subject.id: subject
            for subject in self.list_by_tenant(tenant_id)
            if subject.id in subject_ids
        }

    def find_by_id(
        self,
        subject_id: UUID,
        tenant_id: UUID,
    ) -> Subject | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    tenant_id,
                    name,
                    code,
                    coefficient,
                    active
                FROM subjects
                WHERE id = ?
                AND tenant_id = ?
                """,
                (str(subject_id), str(tenant_id)),
            ).fetchone()

            if row is None:
                return None

            return Subject(
                id=UUID(row["id"]),
                tenant_id=UUID(row["tenant_id"]),
                name=row["name"],
                code=row["code"],
                coefficient=row["coefficient"],
                active=bool(row["active"]),
            )
