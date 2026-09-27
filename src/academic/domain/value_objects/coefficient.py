from dataclasses import dataclass


@dataclass(frozen=True)
class Coefficient:
    value: float

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(
                "Le coefficient doit être supérieur à zéro."
            )