from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CurrencyAmountView:
    currency: str
    amount: Decimal


@dataclass(frozen=True)
class RecoveryRateView:
    currency: str
    rate_percent: Decimal | None


@dataclass(frozen=True)
class ClassHeadcountView:
    class_id: UUID
    class_name: str
    active_students: int


@dataclass(frozen=True)
class ClassFinancialSituationView:
    class_id: UUID
    class_name: str
    expected: tuple[CurrencyAmountView, ...]
    paid: tuple[CurrencyAmountView, ...]
    remaining: tuple[CurrencyAmountView, ...]


@dataclass(frozen=True)
class DirectionDashboardView:
    active_students: int
    headcount_by_class: tuple[ClassHeadcountView, ...]
    expected_amounts: tuple[CurrencyAmountView, ...]
    paid_amounts: tuple[CurrencyAmountView, ...]
    remaining_amounts: tuple[CurrencyAmountView, ...]
    recovery_rates: tuple[RecoveryRateView, ...]
    financial_by_class: tuple[ClassFinancialSituationView, ...]
