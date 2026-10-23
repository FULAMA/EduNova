from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Score:
    value: float
    maximum: float

    def __post_init__(self):
        if not math.isfinite(self.value) or not math.isfinite(self.maximum):
            raise ValueError("La note et son maximum doivent être des nombres finis.")
        if self.maximum <= 0:
            raise ValueError("Le maximum doit etre superieur à zéro")
        if self.value < 0:
            raise ValueError("La note ne peut pas etre négative")
        if self.value > self.maximum:
            raise ValueError("Note ne peut pas dépassé le maximum")

    def normalized_to_20(self) -> float:
        return (self.value / self.maximum) * 20
