from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.billing.application.service import BillingSummary, Charge, CounterEntry, FeeAssignment, FeeType, Payment
from src.billing.domain.money import Currency, Money
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteBillingRepository:
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def student_exists(self, student_id: UUID, tenant_id: UUID) -> bool:
        with self._database.connect() as connection:
            return connection.execute(
                "SELECT 1 FROM students WHERE id = ? AND tenant_id = ?",
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

    def create_fee_type(self, tenant_id, name, description, category, money, academic_period_id, applicability, actor_id):
        now = datetime.now().astimezone()
        fee_type = FeeType(uuid4(), tenant_id, name, description, category, money, academic_period_id, applicability, "DRAFT", 1, actor_id, now, now)
        with self._database.connect() as connection:
            connection.execute("""INSERT INTO billing_fee_types
                (id, tenant_id, name, description, category, amount, currency, academic_period_id,
                 applicability, status, version, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(fee_type.id), str(tenant_id), name, description, category, str(money.amount), money.currency.value,
                 str(academic_period_id) if academic_period_id else None, applicability, fee_type.status,
                 fee_type.version, str(actor_id), now.isoformat(), now.isoformat()))
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
            fee = connection.execute("SELECT * FROM billing_fee_types WHERE tenant_id = ? AND id = ?", (str(tenant_id), str(fee_type_id))).fetchone()
            if fee is None:
                raise LookupError("Type de frais introuvable dans cet etablissement.")
            if fee["status"] != "PUBLISHED":
                raise ValueError("Seul un type de frais publie peut etre attribue.")
            if fee["academic_period_id"] and str(academic_period_id) != fee["academic_period_id"]:
                raise ValueError("La periode ne correspond pas au type de frais.")
            student = connection.execute("SELECT 1 FROM students WHERE tenant_id = ? AND id = ?", (str(tenant_id), str(student_id))).fetchone()
            if student is None:
                raise LookupError("Eleve introuvable dans cet etablissement.")
            existing = connection.execute("SELECT a.*, f.amount, f.currency FROM billing_fee_assignments a JOIN billing_fee_types f ON f.tenant_id = a.tenant_id AND f.id = a.fee_type_id WHERE a.tenant_id = ? AND a.fee_type_id = ? AND a.student_id = ? AND COALESCE(a.academic_period_id, '') = COALESCE(?, '')", (str(tenant_id), str(fee_type_id), str(student_id), str(academic_period_id) if academic_period_id else None)).fetchone()
            if existing is not None:
                return self._fee_assignment(existing)
            now = datetime.now().astimezone()
            assignment_id, charge_id = uuid4(), uuid4()
            connection.execute("INSERT INTO billing_charges (id, tenant_id, student_id, description, amount, currency, due_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')", (str(charge_id), str(tenant_id), str(student_id), fee["name"], fee["amount"], fee["currency"], None))
            connection.execute("""INSERT INTO billing_fee_assignments
                (id, tenant_id, fee_type_id, fee_type_version, student_id, academic_period_id, charge_id, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (str(assignment_id), str(tenant_id), str(fee_type_id), fee["version"], str(student_id), str(academic_period_id) if academic_period_id else None, str(charge_id), str(actor_id), now.isoformat()))
            row = connection.execute("SELECT a.*, f.amount, f.currency FROM billing_fee_assignments a JOIN billing_fee_types f ON f.tenant_id = a.tenant_id AND f.id = a.fee_type_id WHERE a.tenant_id = ? AND a.id = ?", (str(tenant_id), str(assignment_id))).fetchone()
        return self._fee_assignment(row)

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
        return FeeType(UUID(row["id"]), UUID(row["tenant_id"]), row["name"], row["description"], row["category"], Money(Decimal(row["amount"]), Currency(row["currency"])), UUID(row["academic_period_id"]) if row["academic_period_id"] else None, row["applicability"], row["status"], row["version"], UUID(row["created_by"]), datetime.fromisoformat(row["created_at"]), datetime.fromisoformat(row["updated_at"]))

    @staticmethod
    def _fee_assignment(row):
        return FeeAssignment(UUID(row["id"]), UUID(row["tenant_id"]), UUID(row["fee_type_id"]), row["fee_type_version"], UUID(row["student_id"]), UUID(row["academic_period_id"]) if row["academic_period_id"] else None, UUID(row["charge_id"]), Money(Decimal(row["amount"]), Currency(row["currency"])), UUID(row["created_by"]), datetime.fromisoformat(row["created_at"]))

    @staticmethod
    def _charge(row) -> Charge:
        return Charge(UUID(row["id"]), UUID(row["tenant_id"]), UUID(row["student_id"]), row["description"], Money(Decimal(row["amount"]), Currency(row["currency"])), date.fromisoformat(row["due_date"]) if row["due_date"] else None, row["status"])

    @staticmethod
    def _payment(row) -> Payment:
        return Payment(UUID(row["id"]), UUID(row["tenant_id"]), UUID(row["charge_id"]), UUID(row["student_id"]), Money(Decimal(row["amount"]), Currency(row["currency"])), row["idempotency_key"], row["status"], UUID(row["recorded_by"]), datetime.fromisoformat(row["recorded_at"]), row["receipt_number"], row["receipt_status"] if "receipt_status" in row.keys() else "ISSUED")

