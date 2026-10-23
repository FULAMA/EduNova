from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Coefficient:
    value: float

    def __post_init__(self):
        if not math.isfinite(self.value):
            raise ValueError("Le coefficient doit être un nombre fini.")
        if self.value <= 0:
            raise ValueError(
                "Le coefficient doit être supérieur à zéro."
            )
