from uuid import UUID

from src.application.interfaces.subject_repository import SubjectRepository
from src.domain.entities.subject import Subject
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
                    name,
                    code,
                    coefficient,
                    active
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(subject.id),
                    subject.name,
                    subject.code,
                    subject.coefficient,
                    int(subject.active),
                ),
            )

    def find_by_id(
        self,
        subject_id: UUID,
    ) -> Subject | None:

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    name,
                    code,
                    coefficient,
                    active
                FROM subjects
                WHERE id = ?
                """,
                (str(subject_id),),
            ).fetchone()

            if row is None:
                return None

            return Subject(
                id=UUID(row["id"]),
                name=row["name"],
                code=row["code"],
                coefficient=row["coefficient"],
                active=bool(row["active"]),
            )
