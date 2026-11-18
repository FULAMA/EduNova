from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.billing.domain.money import Currency


class CurrencyAmount(BaseModel):
    currency: Currency
    amount: Decimal


class RecoveryRate(BaseModel):
    currency: Currency
    rate_percent: Decimal | None


class ClassHeadcount(BaseModel):
    class_id: UUID
    class_name: str
    active_students: int


class ClassFinancialSituation(BaseModel):
    class_id: UUID
    class_name: str
    expected: list[CurrencyAmount]
    paid: list[CurrencyAmount]
    remaining: list[CurrencyAmount]


class DirectionDashboardResponse(BaseModel):
    active_students: int
    headcount_by_class: list[ClassHeadcount]
    expected_amounts: list[CurrencyAmount]
    paid_amounts: list[CurrencyAmount]
    remaining_amounts: list[CurrencyAmount]
    recovery_rates: list[RecoveryRate]
    financial_by_class: list[ClassFinancialSituation]
