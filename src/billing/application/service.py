from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.billing.domain.money import Currency, Money


@dataclass(frozen=True)
class Charge:
    id: UUID
    tenant_id: UUID
    student_id: UUID
    description: str
    amount: Money
    due_date: date | None
    status: str = "OPEN"


@dataclass(frozen=True)
class FeeType:
    id: UUID
    tenant_id: UUID
    name: str
    description: str
    category: str
    amount: Money
    academic_period_id: UUID | None
    target_class_id: UUID | None
    applicability: str
    status: str
    version: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class FeeAssignment:
    id: UUID
    tenant_id: UUID
    fee_type_id: UUID
    fee_type_version: int
    student_id: UUID
    academic_period_id: UUID | None
    snapshot_class_id: UUID | None
    charge_id: UUID
    amount: Money
    created_by: UUID
    created_at: datetime


@dataclass(frozen=True)
class Payment:
    id: UUID
    tenant_id: UUID
    charge_id: UUID
    student_id: UUID
    amount: Money
    idempotency_key: str
    status: str
    recorded_by: UUID
    recorded_at: datetime
    receipt_number: str
    receipt_status: str = "ISSUED"


@dataclass(frozen=True)
class CounterEntry:
    id: UUID
    tenant_id: UUID
    original_payment_id: UUID
    amount: Money
    reason: str
    recorded_by: UUID
    recorded_at: datetime


@dataclass(frozen=True)
class BillingSummary:
    charges: tuple[Charge, ...]
    payments: tuple[Payment, ...]


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

    def reverse_payment(self, tenant_id: UUID, payment_id: UUID, reason: str, actor_id: UUID) -> CounterEntry:
        if not reason.strip():
            raise ValueError("Le motif de correction est obligatoire.")
        return self._repository.reverse_payment(tenant_id, payment_id, reason.strip(), actor_id)

    def receipt_pdf(self, tenant_id: UUID, receipt_number: str):
        receipt = self._repository.receipt_by_number(tenant_id, receipt_number)
        if receipt is None:
            raise LookupError("Recu introuvable dans cet etablissement.")
        return receipt

