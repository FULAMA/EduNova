from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum


class Currency(StrEnum):
    USD = "USD"
    CDF = "CDF"


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        try:
            value = Decimal(self.amount)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("Le montant est invalide.") from exc
        if not value.is_finite() or value <= 0:
            raise ValueError("Le montant doit etre strictement positif.")
        if value.as_tuple().exponent < -2:
            raise ValueError("Le montant ne peut pas depasser deux decimales.")
        object.__setattr__(self, "amount", value.quantize(Decimal("0.01")))

