import json
from datetime import datetime
from uuid import UUID

from src.academic.application.interfaces.report_card_repository import ReportCardRepository
from src.academic.domain.entities.report_card import ReportCard, ReportCardStatus
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteReportCardRepository(ReportCardRepository):
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save(self, report_card: ReportCard) -> ReportCard:
        if report_card.id is None:
            raise ValueError("Un identifiant de bulletin est obligatoire.")
        with self._database.connect() as connection:
            connection.execute("""INSERT INTO report_cards
                (id, tenant_id, student_id, academic_period_id, deliberation_id,
                 deliberation_version, record_version, report_version, status,
                 snapshot_json, snapshot_hash, created_at, issued_at, issued_by,
                 previous_report_card_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                str(report_card.id), str(report_card.tenant_id), str(report_card.student_id),
                str(report_card.academic_period_id), str(report_card.deliberation_id),
                report_card.deliberation_version, report_card.record_version,
                report_card.report_version, report_card.status.value,
                json.dumps(report_card.snapshot, sort_keys=True), report_card.snapshot_hash,
                report_card.created_at.isoformat() if report_card.created_at else datetime.utcnow().isoformat(),
                report_card.issued_at.isoformat() if report_card.issued_at else None,
                str(report_card.issued_by) if report_card.issued_by else None,
                str(report_card.previous_report_card_id) if report_card.previous_report_card_id else None,
            ))
        return report_card

    def find_by_id(self, report_card_id: UUID, tenant_id: UUID) -> ReportCard | None:
        with self._database.connect() as connection:
            row = connection.execute("SELECT * FROM report_cards WHERE tenant_id=? AND id=?", (str(tenant_id), str(report_card_id))).fetchone()
        return self._to_domain(row) if row else None

    def list_published_for_student(self, tenant_id: UUID, student_id: UUID) -> tuple[ReportCard, ...]:
        with self._database.connect() as connection:
            rows = connection.execute("""SELECT * FROM report_cards
                WHERE tenant_id=? AND student_id=? AND status='ISSUED'
                ORDER BY academic_period_id, report_version DESC""", (str(tenant_id), str(student_id))).fetchall()
        return tuple(self._to_domain(row) for row in rows)

    def find_published_for_student(self, report_card_id: UUID, tenant_id: UUID, student_id: UUID) -> ReportCard | None:
        with self._database.connect() as connection:
            row = connection.execute("""SELECT * FROM report_cards
                WHERE tenant_id=? AND student_id=? AND id=? AND status='ISSUED'""", (str(tenant_id), str(student_id), str(report_card_id))).fetchone()
        return self._to_domain(row) if row else None

    def publish(self, report_card_id: UUID, tenant_id: UUID, actor_id: UUID, published_at) -> ReportCard:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute("""SELECT 1 FROM report_cards current
                WHERE current.tenant_id=? AND current.status='ISSUED'
                  AND current.student_id=(SELECT student_id FROM report_cards WHERE tenant_id=? AND id=? LIMIT 1)
                  AND current.academic_period_id=(SELECT academic_period_id FROM report_cards WHERE tenant_id=? AND id=? LIMIT 1)""",
                (str(tenant_id), str(tenant_id), str(report_card_id), str(tenant_id), str(report_card_id))).fetchone()
            if existing is not None:
                raise ValueError("Une version publiee existe deja; utilisez la correction versionnee.")
            cursor = connection.execute("""UPDATE report_cards
                SET status='ISSUED', issued_at=?, issued_by=?
                WHERE tenant_id=? AND id=? AND status='DRAFT'""", (published_at.isoformat(), str(actor_id), str(tenant_id), str(report_card_id)))
            if cursor.rowcount != 1:
                raise ValueError("Le bulletin est deja emis ou introuvable.")
            row = connection.execute("SELECT * FROM report_cards WHERE tenant_id=? AND id=?", (str(tenant_id), str(report_card_id))).fetchone()
        return self._to_domain(row)

    def replace_with_correction(self, previous: ReportCard, replacement: ReportCard) -> ReportCard:
        if previous.status is not ReportCardStatus.ISSUED or replacement.status is not ReportCardStatus.ISSUED:
            raise ValueError("Un remplacement exige deux versions coherentes.")
        if replacement.previous_report_card_id != previous.id or replacement.report_version != previous.report_version + 1:
            raise ValueError("La nouvelle version du bulletin est incoherente.")
        if replacement.issued_at is None or replacement.issued_by is None:
            raise ValueError("Un bulletin emis doit avoir un auteur et une date.")
        created_at = replacement.created_at or datetime.utcnow()
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "UPDATE report_cards SET status='SUPERSEDED' WHERE tenant_id=? AND id=? AND status='ISSUED'",
                (str(previous.tenant_id), str(previous.id)),
            )
            if cursor.rowcount != 1:
                raise ValueError("Le bulletin a deja ete remplace.")
            try:
                connection.execute("""INSERT INTO report_cards
                    (id, tenant_id, student_id, academic_period_id, deliberation_id,
                     deliberation_version, record_version, report_version, status,
                     snapshot_json, snapshot_hash, created_at, issued_at, issued_by,
                     previous_report_card_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                    str(replacement.id), str(replacement.tenant_id), str(replacement.student_id),
                    str(replacement.academic_period_id), str(replacement.deliberation_id),
                    replacement.deliberation_version, replacement.record_version,
                    replacement.report_version, replacement.status.value,
                    json.dumps(replacement.snapshot, sort_keys=True), replacement.snapshot_hash,
                    created_at.isoformat(), replacement.issued_at.isoformat(),
                    str(replacement.issued_by), str(replacement.previous_report_card_id),
                ))
            except Exception as exc:
                raise ValueError("La correction du bulletin n a pas ete enregistree.") from exc
            row = connection.execute(
                "SELECT * FROM report_cards WHERE tenant_id=? AND id=?",
                (str(replacement.tenant_id), str(replacement.id)),
            ).fetchone()
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row) -> ReportCard:
        snapshot = json.loads(row["snapshot_json"])
        if ReportCard.calculate_snapshot_hash(snapshot) != row["snapshot_hash"]:
            raise ValueError("Le snapshot du bulletin est corrompu.")
        return ReportCard(
            tenant_id=UUID(row["tenant_id"]), student_id=UUID(row["student_id"]),
            academic_period_id=UUID(row["academic_period_id"]), deliberation_id=UUID(row["deliberation_id"]),
            deliberation_version=row["deliberation_version"], record_version=row["record_version"],
            report_version=row["report_version"], status=ReportCardStatus(row["status"]),
            snapshot=snapshot, snapshot_hash=row["snapshot_hash"],
            id=UUID(row["id"]), created_at=datetime.fromisoformat(row["created_at"]),
            issued_at=datetime.fromisoformat(row["issued_at"]) if row["issued_at"] else None,
            issued_by=UUID(row["issued_by"]) if row["issued_by"] else None,
            previous_report_card_id=UUID(row["previous_report_card_id"]) if row["previous_report_card_id"] else None,
        )
