from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from src.billing.domain.money import Currency, Money
from src.billing.domain.entities import (
    Charge,
    CounterEntry,
    FeeAssignment,
    FeeReminder,
    FeeType,
    Payment,
)


@dataclass(frozen=True)
class ClassFeeAssignmentResult:
    fee_type_id: UUID
    class_id: UUID
    academic_period_id: UUID
    total_eligible_students: int
    assigned_count: int
    already_assigned_count: int
    assignments: tuple[FeeAssignment, ...]


@dataclass(frozen=True)
class BillingSummary:
    charges: tuple[Charge, ...]
    payments: tuple[Payment, ...]


@dataclass(frozen=True)
class PaymentPage:
    items: tuple[Payment, ...]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class ArrearItem:
    charge_id: UUID
    student_id: UUID
    description: str
    currency: Currency
    amount_due: Decimal
    amount_paid: Decimal
    amount_remaining: Decimal
    due_date: date | None
    charge_status: str
    overdue: bool
    class_id: UUID | None = None


@dataclass(frozen=True)
class ArrearPage:
    items: tuple[ArrearItem, ...]
    total: int
    limit: int
    offset: int


class BillingService:
    def __init__(self, repository):
        self._repository = repository

    def create_charge(
        self,
        tenant_id: UUID,
        student_id: UUID,
        description: str,
        amount: Decimal,
        currency: Currency,
        due_date: date | None,
    ) -> Charge:
        if not description.strip():
            raise ValueError("La description des frais est obligatoire.")
        if not self._repository.student_exists(student_id, tenant_id):
            raise LookupError("Eleve introuvable dans cet etablissement.")
        charge = Charge(
            id=uuid4(), tenant_id=tenant_id, student_id=student_id,
            description=description.strip(), amount=Money(amount, currency),
            due_date=due_date,
        )
        self._repository.save_charge(charge)
        return charge

    def create_fee_type(self, tenant_id: UUID, name: str, description: str, category: str,
                        amount: Decimal, currency: Currency, academic_period_id: UUID | None,
                        applicability: str, actor_id: UUID, target_class_id: UUID | None = None) -> FeeType:
        if not name.strip() or not category.strip():
            raise ValueError("Le nom et la categorie sont obligatoires.")
        if applicability not in {"ESTABLISHMENT", "CLASS", "STUDENT"}:
            raise ValueError("Regle d applicabilite invalide.")
        if applicability == "CLASS" and target_class_id is None:
            raise ValueError("Une classe cible est obligatoire pour un frais CLASS.")
        if applicability != "CLASS" and target_class_id is not None:
            raise ValueError("Une classe cible est reservee aux frais CLASS.")
        return self._repository.create_fee_type(
            tenant_id, name.strip(), description.strip(), category.strip(),
            Money(amount, currency), academic_period_id, applicability, actor_id,
            target_class_id,
        )

    def list_fee_types(self, tenant_id: UUID) -> tuple[FeeType, ...]:
        return self._repository.list_fee_types(tenant_id)

    def change_fee_type_status(self, tenant_id: UUID, fee_type_id: UUID, status: str, actor_id: UUID) -> FeeType:
        if status not in {"PUBLISHED", "ARCHIVED"}:
            raise ValueError("Statut de catalogue invalide.")
        return self._repository.change_fee_type_status(tenant_id, fee_type_id, status, actor_id)

    def assign_fee_type(self, tenant_id: UUID, fee_type_id: UUID, student_id: UUID, academic_period_id: UUID | None, actor_id: UUID) -> FeeAssignment:
        return self._repository.assign_fee_type(tenant_id, fee_type_id, student_id, academic_period_id, actor_id)

    def assign_fee_type_to_class(
        self,
        tenant_id: UUID,
        fee_type_id: UUID,
        class_id: UUID,
        academic_period_id: UUID,
        actor_id: UUID,
    ) -> ClassFeeAssignmentResult:
        return self._repository.assign_fee_type_to_class(
            tenant_id, fee_type_id, class_id, academic_period_id, actor_id
        )


    def record_payment(
        self,
        tenant_id: UUID,
        charge_id: UUID,
        amount: Decimal,
        currency: Currency,
        idempotency_key: str,
        actor_id: UUID,
    ) -> Payment:
        if not idempotency_key.strip():
            raise ValueError("La cle d idempotence est obligatoire.")
        payment = self._repository.record_payment(
            tenant_id, charge_id, Money(amount, currency), idempotency_key.strip(), actor_id
        )
        return payment

    def summary(self, tenant_id: UUID, student_id: UUID) -> BillingSummary:
        if not self._repository.student_exists(student_id, tenant_id):
            raise LookupError("Eleve introuvable dans cet etablissement.")
        return self._repository.summary(tenant_id, student_id)

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
    ) -> PaymentPage:
        if limit < 1 or limit > 200:
            raise ValueError("La limite de pagination doit etre entre 1 et 200.")
        if offset < 0:
            raise ValueError("Le decalage de pagination ne peut pas etre negatif.")
        if status is not None and not status.strip():
            raise ValueError("Le statut de paiement est invalide.")
        if student_id is not None and not self._repository.student_exists(
            student_id, tenant_id
        ):
            raise LookupError("Eleve introuvable dans cet etablissement.")
        items, total = self._repository.list_payments(
            tenant_id,
            student_id=student_id,
            class_id=class_id,
            status=status.strip() if status else None,
            recorded_from=recorded_from,
            recorded_to=recorded_to,
            limit=limit,
            offset=offset,
        )
        return PaymentPage(items=items, total=total, limit=limit, offset=offset)

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
    ) -> ArrearPage:
        if limit < 1 or limit > 200:
            raise ValueError("La limite de pagination doit etre entre 1 et 200.")
        if offset < 0:
            raise ValueError("Le decalage de pagination ne peut pas etre negatif.")
        if student_id is not None and not self._repository.student_exists(
            student_id, tenant_id
        ):
            raise LookupError("Eleve introuvable dans cet etablissement.")
        items, total = self._repository.list_arrears(
            tenant_id,
            student_id=student_id,
            class_id=class_id,
            as_of=as_of,
            overdue_only=overdue_only,
            limit=limit,
            offset=offset,
        )
        return ArrearPage(items=items, total=total, limit=limit, offset=offset)

    def reverse_payment(self, tenant_id: UUID, payment_id: UUID, reason: str, actor_id: UUID) -> CounterEntry:
        if not reason.strip():
            raise ValueError("Le motif de correction est obligatoire.")
        return self._repository.reverse_payment(tenant_id, payment_id, reason.strip(), actor_id)

    def receipt_pdf(self, tenant_id: UUID, receipt_number: str):
        receipt = self._repository.receipt_by_number(tenant_id, receipt_number)
        if receipt is None:
            raise LookupError("Recu introuvable dans cet etablissement.")
        return receipt

    def record_arrear_reminder(
        self,
        tenant_id: UUID,
        charge_id: UUID,
        channel: str,
        recipient: str,
        notes: str | None,
        actor_id: UUID,
    ) -> FeeReminder:
        channel_clean = channel.strip().upper()
        allowed_channels = {"SMS", "EMAIL", "LETTER", "PHONE", "IN_PERSON"}
        if channel_clean not in allowed_channels:
            raise ValueError(f"Canal de relance invalide. Autorises : {', '.join(sorted(allowed_channels))}")
        if not recipient.strip():
            raise ValueError("Le destinataire de la relance est obligatoire.")
        return self._repository.record_arrear_reminder(
            tenant_id, charge_id, channel_clean, recipient.strip(), notes.strip() if notes else None, actor_id
        )

    def list_arrear_reminders(
        self,
        tenant_id: UUID,
        charge_id: UUID,
    ) -> tuple[FeeReminder, ...]:
        return self._repository.list_arrear_reminders(tenant_id, charge_id)
