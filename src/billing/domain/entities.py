from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.billing.domain.money import Money


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
class FeeReminder:
    id: UUID
    tenant_id: UUID
    charge_id: UUID
    student_id: UUID
    channel: str
    recipient: str
    notes: str | None
    sent_at: datetime
    sent_by: UUID
