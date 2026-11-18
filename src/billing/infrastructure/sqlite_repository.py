from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.billing.application.service import (
    ArrearItem,
    BillingSummary,
    ClassFeeAssignmentResult,
)
from src.billing.domain.entities import (
    Charge,
    CounterEntry,
    FeeAssignment,
    FeeReminder,
    FeeType,
    Payment,
)
from src.billing.domain.money import Currency, Money
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteBillingRepository:
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def student_exists(self, student_id: UUID, tenant_id: UUID) -> bool:
        with self._database.connect() as connection:
            return connection.execute(
                "SELECT 1 FROM students WHERE id = ? AND tenant_id = ? AND active = 1",
                (str(student_id), str(tenant_id)),
            ).fetchone() is not None

    def save_charge(self, charge: Charge) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """INSERT INTO billing_charges
                (id, tenant_id, student_id, description, amount, currency, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(charge.id), str(charge.tenant_id), str(charge.student_id),
                 charge.description, str(charge.amount.amount), charge.amount.currency.value,
                 charge.due_date.isoformat() if charge.due_date else None, charge.status),
            )

    def create_fee_type(
        self, tenant_id, name, description, category, money, academic_period_id,
        applicability, actor_id, target_class_id=None,
    ):
        now = datetime.now().astimezone()
        fee_type = FeeType(
            uuid4(), tenant_id, name, description, category, money,
            academic_period_id, target_class_id, applicability, "DRAFT", 1,
            actor_id, now, now,
        )
        with self._database.connect() as connection:
            if academic_period_id is not None:
                period = connection.execute(
                    "SELECT 1 FROM academic_periods WHERE tenant_id = ? AND id = ?",
                    (str(tenant_id), str(academic_period_id)),
                ).fetchone()
                if period is None:
                    raise LookupError("Periode scolaire introuvable dans cet etablissement.")
            if target_class_id is not None:
                target_class = connection.execute(
                    "SELECT 1 FROM academic_classes WHERE tenant_id = ? AND id = ?",
                    (str(tenant_id), str(target_class_id)),
                ).fetchone()
                if target_class is None:
                    raise LookupError("Classe cible introuvable dans cet etablissement.")
            connection.execute("""INSERT INTO billing_fee_types
                (id, tenant_id, name, description, category, amount, currency,
                 academic_period_id, applicability, target_class_id, status,
                 version, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(fee_type.id), str(tenant_id), name, description, category,
                 str(money.amount), money.currency.value,
                 str(academic_period_id) if academic_period_id else None,
                 applicability, str(target_class_id) if target_class_id else None,
                 fee_type.status, fee_type.version, str(actor_id),
                 now.isoformat(), now.isoformat()))
        return fee_type

    def list_fee_types(self, tenant_id):
        with self._database.connect() as connection:
            rows = connection.execute("SELECT * FROM billing_fee_types WHERE tenant_id = ? ORDER BY created_at, id", (str(tenant_id),)).fetchall()
        return tuple(self._fee_type(row) for row in rows)

    def change_fee_type_status(self, tenant_id, fee_type_id, status, actor_id):
        with self._database.connect() as connection:
            row = connection.execute("SELECT * FROM billing_fee_types WHERE tenant_id = ? AND id = ?", (str(tenant_id), str(fee_type_id))).fetchone()
            if row is None:
                raise LookupError("Type de frais introuvable dans cet etablissement.")
            if row["status"] == "ARCHIVED":
                raise ValueError("Un type de frais archive ne peut pas etre reutilise.")
            now = datetime.now().astimezone()
            connection.execute("UPDATE billing_fee_types SET status = ?, version = version + 1, updated_at = ? WHERE tenant_id = ? AND id = ?", (status, now.isoformat(), str(tenant_id), str(fee_type_id)))
            updated = connection.execute("SELECT * FROM billing_fee_types WHERE tenant_id = ? AND id = ?", (str(tenant_id), str(fee_type_id))).fetchone()
        return self._fee_type(updated)

    def assign_fee_type(self, tenant_id, fee_type_id, student_id, academic_period_id, actor_id):
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            fee = connection.execute(
                "SELECT * FROM billing_fee_types WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(fee_type_id)),
            ).fetchone()
            if fee is None:
                raise LookupError("Type de frais introuvable dans cet etablissement.")
            if fee["status"] != "PUBLISHED":
                raise ValueError("Seul un type de frais publie peut etre attribue.")
            if fee["academic_period_id"] and str(academic_period_id) != fee["academic_period_id"]:
                raise ValueError("La periode ne correspond pas au type de frais.")

            student = connection.execute(
                "SELECT 1 FROM students WHERE tenant_id = ? AND id = ? AND active = 1",
                (str(tenant_id), str(student_id)),
            ).fetchone()
            if student is None:
                raise LookupError("Eleve actif introuvable dans cet etablissement.")

            snapshot_class_id = None
            period = None
            if academic_period_id is not None:
                period = connection.execute(
                    "SELECT academic_year_id FROM academic_periods WHERE tenant_id = ? AND id = ?",
                    (str(tenant_id), str(academic_period_id)),
                ).fetchone()
                if period is None:
                    raise LookupError("Periode scolaire introuvable dans cet etablissement.")

            applicability = fee["applicability"]
            if applicability == "ESTABLISHMENT":
                if fee["target_class_id"] is not None:
                    raise ValueError("Un frais ETABLISSEMENT ne peut pas cibler une classe.")
            elif applicability == "CLASS":
                target_class_id = fee["target_class_id"]
                if target_class_id is None:
                    raise ValueError("Ce frais CLASS ne possede pas de classe cible.")
                if academic_period_id is None or period is None or period["academic_year_id"] is None:
                    raise ValueError("Un frais CLASS exige une periode liee a une annee scolaire.")
                target_class = connection.execute(
                    "SELECT 1 FROM academic_classes WHERE tenant_id = ? AND id = ?",
                    (str(tenant_id), target_class_id),
                ).fetchone()
                if target_class is None:
                    raise LookupError("Classe cible introuvable dans cet etablissement.")
                assignment = connection.execute(
                    """SELECT 1 FROM student_assignments
                    WHERE tenant_id = ? AND student_id = ? AND academic_class_id = ?
                      AND academic_year_id = ? AND status = 'ACTIVE'""",
                    (str(tenant_id), str(student_id), target_class_id, period["academic_year_id"]),
                ).fetchone()
                if assignment is None:
                    raise ValueError("L'eleve ne possede pas d'affectation active dans la classe cible pour cette annee scolaire.")
                snapshot_class_id = UUID(target_class_id)
            elif applicability == "STUDENT":
                if fee["target_class_id"] is not None:
                    raise ValueError("Un frais STUDENT ne peut pas cibler une classe.")
            else:
                raise ValueError("Regle d applicabilite invalide.")

            existing = connection.execute(
                """SELECT * FROM billing_fee_assignments
                WHERE tenant_id = ? AND fee_type_id = ? AND student_id = ?
                  AND COALESCE(academic_period_id, '') = COALESCE(?, '')""",
                (str(tenant_id), str(fee_type_id), str(student_id),
                 str(academic_period_id) if academic_period_id else None),
            ).fetchone()
            if existing is not None:
                return self._fee_assignment(existing)

            now = datetime.now().astimezone()
            assignment_id, charge_id = uuid4(), uuid4()
            connection.execute(
                """INSERT INTO billing_charges
                (id, tenant_id, student_id, description, amount, currency, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')""",
                (str(charge_id), str(tenant_id), str(student_id), fee["name"],
                 fee["amount"], fee["currency"], None),
            )
            connection.execute("""INSERT INTO billing_fee_assignments
                (id, tenant_id, fee_type_id, fee_type_version, student_id, academic_period_id,
                 charge_id, created_by, created_at, snapshot_name, snapshot_description,
                 snapshot_category, snapshot_applicability, amount, currency, snapshot_class_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(assignment_id), str(tenant_id), str(fee_type_id), fee["version"],
                 str(student_id), str(academic_period_id) if academic_period_id else None,
                 str(charge_id), str(actor_id), now.isoformat(), fee["name"],
                 fee["description"], fee["category"], fee["applicability"],
                 fee["amount"], fee["currency"],
                 str(snapshot_class_id) if snapshot_class_id else None))
            row = connection.execute(
                "SELECT * FROM billing_fee_assignments WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(assignment_id)),
            ).fetchone()
        return self._fee_assignment(row)


    def assign_fee_type_to_class(
        self,
        tenant_id: UUID,
        fee_type_id: UUID,
        class_id: UUID,
        academic_period_id: UUID,
        actor_id: UUID,
    ) -> ClassFeeAssignmentResult:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            fee = connection.execute(
                "SELECT * FROM billing_fee_types WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(fee_type_id)),
            ).fetchone()
            if fee is None:
                raise LookupError("Type de frais introuvable dans cet etablissement.")
            if fee["status"] != "PUBLISHED":
                raise ValueError("Seul un type de frais publie peut etre attribue.")
            if fee["academic_period_id"] and str(academic_period_id) != fee["academic_period_id"]:
                raise ValueError("La periode ne correspond pas au type de frais.")

            if fee["applicability"] == "CLASS":
                if fee["target_class_id"] and str(fee["target_class_id"]) != str(class_id):
                    raise ValueError("La classe specifiee ne correspond pas a la classe cible du type de frais.")

            target_class = connection.execute(
                "SELECT 1 FROM academic_classes WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(class_id)),
            ).fetchone()
            if target_class is None:
                raise LookupError("Classe cible introuvable dans cet etablissement.")

            period = connection.execute(
                "SELECT academic_year_id FROM academic_periods WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(academic_period_id)),
            ).fetchone()
            if period is None:
                raise LookupError("Periode scolaire introuvable dans cet etablissement.")
            academic_year_id = period["academic_year_id"]
            if academic_year_id is None:
                raise ValueError("La periode scolaire doit etre liee a une annee scolaire.")

            rows = connection.execute(
                """SELECT DISTINCT sa.student_id
                   FROM student_assignments sa
                   JOIN students s ON s.id = sa.student_id AND s.tenant_id = sa.tenant_id
                   WHERE sa.tenant_id = ?
                     AND sa.academic_class_id = ?
                     AND sa.academic_year_id = ?
                     AND sa.status = 'ACTIVE'
                     AND s.active = 1
                   ORDER BY s.last_name, s.first_name""",
                (str(tenant_id), str(class_id), str(academic_year_id)),
            ).fetchall()

            total_eligible = len(rows)
            assigned_count = 0
            already_assigned_count = 0
            assignments = []

            now = datetime.now().astimezone()
            for r in rows:
                st_id = r["student_id"]
                existing = connection.execute(
                    """SELECT * FROM billing_fee_assignments
                    WHERE tenant_id = ? AND fee_type_id = ? AND student_id = ?
                      AND COALESCE(academic_period_id, '') = COALESCE(?, '')""",
                    (str(tenant_id), str(fee_type_id), str(st_id), str(academic_period_id)),
                ).fetchone()

                if existing is not None:
                    already_assigned_count += 1
                    assignments.append(self._fee_assignment(existing))
                    continue

                assignment_id, charge_id = uuid4(), uuid4()
                connection.execute(
                    """INSERT INTO billing_charges
                    (id, tenant_id, student_id, description, amount, currency, due_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')""",
                    (str(charge_id), str(tenant_id), str(st_id), fee["name"],
                     fee["amount"], fee["currency"], now.date().isoformat()),
                )
                snapshot_class_id = str(class_id) if fee["applicability"] == "CLASS" else None
                connection.execute("""INSERT INTO billing_fee_assignments
                    (id, tenant_id, fee_type_id, fee_type_version, student_id, academic_period_id,
                     charge_id, created_by, created_at, snapshot_name, snapshot_description,
                     snapshot_category, snapshot_applicability, amount, currency, snapshot_class_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (str(assignment_id), str(tenant_id), str(fee_type_id), fee["version"],
                     str(st_id), str(academic_period_id) if academic_period_id else None,
                     str(charge_id), str(actor_id), now.isoformat(), fee["name"],
                     fee["description"], fee["category"], fee["applicability"],
                     fee["amount"], fee["currency"], snapshot_class_id))
                assigned_count += 1
                row = connection.execute(
                    "SELECT * FROM billing_fee_assignments WHERE id = ?",
                    (str(assignment_id),),
                ).fetchone()
                assignments.append(self._fee_assignment(row))

            return ClassFeeAssignmentResult(
                fee_type_id=fee_type_id,
                class_id=class_id,
                academic_period_id=academic_period_id,
                total_eligible_students=total_eligible,
                assigned_count=assigned_count,
                already_assigned_count=already_assigned_count,
                assignments=tuple(assignments),
            )

    def record_payment(self, tenant_id: UUID, charge_id: UUID, money: Money,
                       key: str, actor_id: UUID) -> Payment:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            charge_row = connection.execute(
                "SELECT * FROM billing_charges WHERE id = ? AND tenant_id = ?",
                (str(charge_id), str(tenant_id)),
            ).fetchone()
            if charge_row is None:
                raise LookupError("Frais introuvables dans cet etablissement.")
            if charge_row["currency"] != money.currency.value:
                raise ValueError("La devise du paiement ne correspond pas aux frais.")

            existing = connection.execute(
                "SELECT * FROM billing_payments WHERE tenant_id = ? AND idempotency_key = ?",
                (str(tenant_id), key),
            ).fetchone()
            if existing is not None:
                if (existing["charge_id"], existing["amount"], existing["currency"]) != (
                    str(charge_id), str(money.amount), money.currency.value
                ):
                    raise ValueError("La cle d idempotence est deja utilisee avec une autre operation.")
                return self._payment(existing)

            paid = connection.execute(
                "SELECT COALESCE((SELECT SUM(CAST(p.amount AS DECIMAL)) FROM billing_payments p "
                "WHERE p.charge_id = ? AND p.tenant_id = ? AND p.status = 'CONFIRMED'), 0) "
                "- COALESCE((SELECT SUM(CAST(e.amount AS DECIMAL)) FROM billing_counter_entries e "
                "JOIN billing_payments p ON p.tenant_id = e.tenant_id AND p.id = e.original_payment_id "
                "WHERE p.charge_id = ? AND e.tenant_id = ?), 0) AS total",
                (str(charge_id), str(tenant_id), str(charge_id), str(tenant_id)),
            ).fetchone()["total"]
            remaining = Decimal(str(charge_row["amount"])) - Decimal(str(paid))
            if money.amount > remaining:
                raise ValueError("Le paiement depasse le solde restant.")

            payment_id = uuid4()
            recorded_at = datetime.now().astimezone()
            receipt_number = f"REC-{tenant_id.hex[:8]}-{payment_id.hex[:12]}"
            connection.execute(
                """INSERT INTO billing_payments
                (id, tenant_id, charge_id, student_id, amount, currency, idempotency_key,
                 status, recorded_by, recorded_at, receipt_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?, ?, ?)""",
                (str(payment_id), str(tenant_id), charge_row["id"], charge_row["student_id"],
                 str(money.amount), money.currency.value, key, str(actor_id),
                 recorded_at.isoformat(), receipt_number),
            )
            connection.execute(
                """INSERT INTO billing_receipts
                (number, tenant_id, payment_id, amount, currency, issued_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (receipt_number, str(tenant_id), str(payment_id), str(money.amount),
                 money.currency.value, recorded_at.isoformat()),
            )
            row = connection.execute(
                "SELECT * FROM billing_payments WHERE id = ?", (str(payment_id),)
            ).fetchone()
        return self._payment(row)

    def summary(self, tenant_id: UUID, student_id: UUID) -> BillingSummary:
        with self._database.connect() as connection:
            charges = connection.execute(
                "SELECT * FROM billing_charges WHERE tenant_id = ? AND student_id = ? ORDER BY due_date, id",
                (str(tenant_id), str(student_id)),
            ).fetchall()
            payments = connection.execute(
                """SELECT p.*, COALESCE(r.status, 'ISSUED') AS receipt_status
                FROM billing_payments p LEFT JOIN billing_receipts r
                ON r.tenant_id = p.tenant_id AND r.payment_id = p.id
                WHERE p.tenant_id = ? AND p.student_id = ? ORDER BY p.recorded_at, p.id""",
                (str(tenant_id), str(student_id)),
            ).fetchall()
        return BillingSummary(tuple(self._charge(row) for row in charges), tuple(self._payment(row) for row in payments))

    def list_payments(
        self,
        tenant_id: UUID,
        *,
        student_id: UUID | None = None,
        class_id: UUID | None = None,
        status: str | None = None,
        recorded_from: date | None = None,
        recorded_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[tuple[Payment, ...], int]:
        filters = ["p.tenant_id = ?"]
        params: list[object] = [str(tenant_id)]

        if student_id is not None:
            filters.append("p.student_id = ?")
            params.append(str(student_id))
        if status is not None:
            filters.append("p.status = ?")
            params.append(status)
        if recorded_from is not None:
            filters.append("date(p.recorded_at) >= date(?)")
            params.append(recorded_from.isoformat())
        if recorded_to is not None:
            filters.append("date(p.recorded_at) <= date(?)")
            params.append(recorded_to.isoformat())
        if class_id is not None:
            filters.append(
                """EXISTS (
                    SELECT 1 FROM student_assignments sa
                    WHERE sa.tenant_id = p.tenant_id
                      AND sa.student_id = p.student_id
                      AND sa.academic_class_id = ?
                      AND sa.status = 'ACTIVE'
                )"""
            )
            params.append(str(class_id))

        where_clause = " AND ".join(filters)
        with self._database.connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(*) AS total FROM billing_payments p WHERE {where_clause}",
                params,
            ).fetchone()["total"]
            rows = connection.execute(
                f"""
                SELECT p.*, COALESCE(r.status, 'ISSUED') AS receipt_status
                FROM billing_payments p
                LEFT JOIN billing_receipts r
                  ON r.tenant_id = p.tenant_id AND r.payment_id = p.id
                WHERE {where_clause}
                ORDER BY p.recorded_at DESC, p.id DESC
                LIMIT ? OFFSET ?
                """,
                [*params, limit, offset],
            ).fetchall()
        return tuple(self._payment(row) for row in rows), int(total)

    def list_arrears(
        self,
        tenant_id: UUID,
        *,
        student_id: UUID | None = None,
        class_id: UUID | None = None,
        as_of: date | None = None,
        overdue_only: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[tuple[ArrearItem, ...], int]:
        reference = as_of or date.today()
        filters = ["c.tenant_id = ?", "c.status = 'OPEN'"]
        params: list[object] = [str(tenant_id)]

        if student_id is not None:
            filters.append("c.student_id = ?")
            params.append(str(student_id))
        if class_id is not None:
            filters.append(
                """EXISTS (
                    SELECT 1 FROM student_assignments sa
                    WHERE sa.tenant_id = c.tenant_id
                      AND sa.student_id = c.student_id
                      AND sa.academic_class_id = ?
                      AND sa.status = 'ACTIVE'
                )"""
            )
            params.append(str(class_id))

        where_clause = " AND ".join(filters)
        with self._database.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    c.id AS charge_id,
                    c.student_id,
                    c.description,
                    c.currency,
                    CAST(c.amount AS DECIMAL) AS amount_due,
                    c.due_date,
                    c.status AS charge_status,
                    (
                        SELECT sa.academic_class_id
                        FROM student_assignments sa
                        WHERE sa.tenant_id = c.tenant_id
                          AND sa.student_id = c.student_id
                          AND sa.status = 'ACTIVE'
                        ORDER BY sa.updated_at DESC, sa.id DESC
                        LIMIT 1
                    ) AS class_id,
                    COALESCE((
                        SELECT SUM(CAST(p.amount AS DECIMAL))
                        FROM billing_payments p
                        WHERE p.tenant_id = c.tenant_id
                          AND p.charge_id = c.id
                          AND p.status = 'CONFIRMED'
                    ), 0) - COALESCE((
                        SELECT SUM(CAST(e.amount AS DECIMAL))
                        FROM billing_counter_entries e
                        JOIN billing_payments p
                          ON p.tenant_id = e.tenant_id AND p.id = e.original_payment_id
                        WHERE e.tenant_id = c.tenant_id
                          AND p.charge_id = c.id
                    ), 0) AS amount_paid
                FROM billing_charges c
                WHERE {where_clause}
                ORDER BY c.due_date IS NULL, c.due_date, c.id
                """,
                params,
            ).fetchall()

        items: list[ArrearItem] = []
        for row in rows:
            amount_due = Decimal(str(row["amount_due"])).quantize(Decimal("0.01"))
            amount_paid = Decimal(str(row["amount_paid"])).quantize(Decimal("0.01"))
            remaining = (amount_due - amount_paid).quantize(Decimal("0.01"))
            if remaining <= 0:
                continue
            due_date = (
                date.fromisoformat(row["due_date"]) if row["due_date"] else None
            )
            overdue = due_date is not None and due_date < reference
            if overdue_only and not overdue:
                continue
            items.append(
                ArrearItem(
                    charge_id=UUID(row["charge_id"]),
                    student_id=UUID(row["student_id"]),
                    description=row["description"],
                    currency=Currency(row["currency"]),
                    amount_due=amount_due,
                    amount_paid=amount_paid,
                    amount_remaining=remaining,
                    due_date=due_date,
                    charge_status=row["charge_status"],
                    overdue=overdue,
                    class_id=UUID(row["class_id"]) if row["class_id"] else None,
                )
            )

        total = len(items)
        page = tuple(items[offset : offset + limit])
        return page, total

    def reverse_payment(self, tenant_id: UUID, payment_id: UUID, reason: str, actor_id: UUID) -> CounterEntry:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            payment = connection.execute("SELECT * FROM billing_payments WHERE id = ? AND tenant_id = ?", (str(payment_id), str(tenant_id))).fetchone()
            if payment is None:
                raise LookupError("Paiement introuvable dans cet etablissement.")
            if payment["status"] != "CONFIRMED":
                raise ValueError("Seul un paiement confirme peut etre corrige.")
            if connection.execute("SELECT 1 FROM billing_counter_entries WHERE tenant_id = ? AND original_payment_id = ?", (str(tenant_id), str(payment_id))).fetchone() is not None:
                raise ValueError("Ce paiement a deja ete corrige.")
            entry_id = uuid4()
            recorded_at = datetime.now().astimezone()
            connection.execute("""INSERT INTO billing_counter_entries
                (id, tenant_id, original_payment_id, amount, currency, reason, recorded_by, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (str(entry_id), str(tenant_id), str(payment_id), payment["amount"], payment["currency"], reason, str(actor_id), recorded_at.isoformat()))
            connection.execute("UPDATE billing_receipts SET status = 'REVERSED', reversed_by_entry_id = ? WHERE tenant_id = ? AND payment_id = ?", (str(entry_id), str(tenant_id), str(payment_id)))
        return CounterEntry(entry_id, tenant_id, payment_id, Money(Decimal(payment["amount"]), Currency(payment["currency"])), reason, actor_id, recorded_at)

    def receipt_by_number(self, tenant_id: UUID, number: str):
        with self._database.connect() as connection:
            return connection.execute("""SELECT r.*, p.recorded_by, p.charge_id, p.student_id
                FROM billing_receipts r JOIN billing_payments p ON p.tenant_id = r.tenant_id AND p.id = r.payment_id
                WHERE r.tenant_id = ? AND r.number = ?""", (str(tenant_id), number)).fetchone()

    @staticmethod
    def _fee_type(row):
        return FeeType(UUID(row["id"]), UUID(row["tenant_id"]), row["name"], row["description"], row["category"], Money(Decimal(row["amount"]), Currency(row["currency"])), UUID(row["academic_period_id"]) if row["academic_period_id"] else None, UUID(row["target_class_id"]) if row["target_class_id"] else None, row["applicability"], row["status"], row["version"], UUID(row["created_by"]), datetime.fromisoformat(row["created_at"]), datetime.fromisoformat(row["updated_at"]))

    @staticmethod
    def _fee_assignment(row):
        return FeeAssignment(UUID(row["id"]), UUID(row["tenant_id"]), UUID(row["fee_type_id"]), row["fee_type_version"], UUID(row["student_id"]), UUID(row["academic_period_id"]) if row["academic_period_id"] else None, UUID(row["snapshot_class_id"]) if row["snapshot_class_id"] else None, UUID(row["charge_id"]), Money(Decimal(row["amount"]), Currency(row["currency"])), UUID(row["created_by"]), datetime.fromisoformat(row["created_at"]))

    @staticmethod
    def _charge(row) -> Charge:
        return Charge(UUID(row["id"]), UUID(row["tenant_id"]), UUID(row["student_id"]), row["description"], Money(Decimal(row["amount"]), Currency(row["currency"])), date.fromisoformat(row["due_date"]) if row["due_date"] else None, row["status"])

    @staticmethod
    def _payment(row) -> Payment:
        return Payment(UUID(row["id"]), UUID(row["tenant_id"]), UUID(row["charge_id"]), UUID(row["student_id"]), Money(Decimal(row["amount"]), Currency(row["currency"])), row["idempotency_key"], row["status"], UUID(row["recorded_by"]), datetime.fromisoformat(row["recorded_at"]), row["receipt_number"], row["receipt_status"] if "receipt_status" in row.keys() else "ISSUED")

    @staticmethod
    def _fee_reminder(row) -> FeeReminder:
        return FeeReminder(
            id=UUID(row["id"]),
            tenant_id=UUID(row["tenant_id"]),
            charge_id=UUID(row["charge_id"]),
            student_id=UUID(row["student_id"]),
            channel=row["channel"],
            recipient=row["recipient"],
            notes=row["notes"],
            sent_at=datetime.fromisoformat(row["sent_at"]),
            sent_by=UUID(row["sent_by"]),
        )

    def record_arrear_reminder(
        self,
        tenant_id: UUID,
        charge_id: UUID,
        channel: str,
        recipient: str,
        notes: str | None,
        actor_id: UUID,
    ) -> FeeReminder:
        now = datetime.now().astimezone()
        reminder_id = uuid4()
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            charge = connection.execute(
                "SELECT * FROM billing_charges WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(charge_id)),
            ).fetchone()
            if charge is None:
                raise LookupError("Frais introuvable dans cet etablissement.")
            if charge["status"] != "OPEN":
                raise ValueError("Impossible d enregistrer une relance pour des frais annules.")

            amount_due = Decimal(str(charge["amount"])).quantize(Decimal("0.01"))
            paid_row = connection.execute(
                """SELECT COALESCE(SUM(CAST(p.amount AS DECIMAL)), 0) AS total_paid
                FROM billing_payments p
                WHERE p.tenant_id = ? AND p.charge_id = ? AND p.status = 'CONFIRMED'""",
                (str(tenant_id), str(charge_id)),
            ).fetchone()
            reversal_row = connection.execute(
                """SELECT COALESCE(SUM(CAST(e.amount AS DECIMAL)), 0) AS total_reversed
                FROM billing_counter_entries e
                JOIN billing_payments p ON p.tenant_id = e.tenant_id AND p.id = e.original_payment_id
                WHERE e.tenant_id = ? AND p.charge_id = ?""",
                (str(tenant_id), str(charge_id)),
            ).fetchone()
            amount_paid = Decimal(str(paid_row["total_paid"])) - Decimal(str(reversal_row["total_reversed"]))
            remaining = (amount_due - amount_paid).quantize(Decimal("0.01"))
            if remaining <= 0:
                raise ValueError("Ces frais ne presentent aucun arriere impaye.")

            connection.execute(
                """INSERT INTO billing_fee_reminders
                (id, tenant_id, charge_id, student_id, channel, recipient, notes, sent_at, sent_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(reminder_id),
                    str(tenant_id),
                    str(charge_id),
                    charge["student_id"],
                    channel,
                    recipient,
                    notes,
                    now.isoformat(),
                    str(actor_id),
                ),
            )
            row = connection.execute(
                "SELECT * FROM billing_fee_reminders WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(reminder_id)),
            ).fetchone()
        return self._fee_reminder(row)

    def list_arrear_reminders(self, tenant_id: UUID, charge_id: UUID) -> tuple[FeeReminder, ...]:
        with self._database.connect() as connection:
            charge = connection.execute(
                "SELECT 1 FROM billing_charges WHERE tenant_id = ? AND id = ?",
                (str(tenant_id), str(charge_id)),
            ).fetchone()
            if charge is None:
                raise LookupError("Frais introuvable dans cet etablissement.")
            rows = connection.execute(
                """SELECT * FROM billing_fee_reminders
                WHERE tenant_id = ? AND charge_id = ?
                ORDER BY sent_at DESC, id DESC""",
                (str(tenant_id), str(charge_id)),
            ).fetchall()
        return tuple(self._fee_reminder(row) for row in rows)

