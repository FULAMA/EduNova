from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.billing.domain.money import Currency


class ChargeCreateRequest(BaseModel):
    student_id: UUID
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: Currency
    due_date: date | None = None


class FeeTypeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    category: str = Field(min_length=1, max_length=80)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: Currency
    academic_period_id: UUID | None = None
    applicability: str = "ESTABLISHMENT"


class ChargeResponse(BaseModel):
    id: UUID
    student_id: UUID
    description: str
    amount: Decimal
    currency: Currency
    due_date: date | None
    status: str


class PaymentCreateRequest(BaseModel):
    charge_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: Currency
    idempotency_key: str = Field(min_length=1, max_length=120)


class PaymentResponse(BaseModel):
    id: UUID
    charge_id: UUID
    student_id: UUID
    amount: Decimal
    currency: Currency
    idempotency_key: str
    status: str
    recorded_by: UUID
    recorded_at: datetime
    receipt_number: str
    receipt_status: str


class PaymentCorrectionRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class CounterEntryResponse(BaseModel):
    id: UUID
    original_payment_id: UUID
    amount: Decimal
    currency: Currency
    reason: str
    recorded_by: UUID
    recorded_at: datetime


class BillingSummaryResponse(BaseModel):
    charges: list[ChargeResponse]
    payments: list[PaymentResponse]


class FeeTypeResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    amount: Decimal
    currency: Currency
    academic_period_id: UUID | None
    applicability: str
    status: str
    version: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class FeeAssignmentRequest(BaseModel):
    student_id: UUID
    academic_period_id: UUID | None = None


class FeeAssignmentResponse(BaseModel):
    id: UUID
    fee_type_id: UUID
    fee_type_version: int
    student_id: UUID
    academic_period_id: UUID | None
    charge_id: UUID
    amount: Decimal
    currency: Currency
    created_by: UUID
    created_at: datetime

