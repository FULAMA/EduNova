from dataclasses import dataclass

@dataclass(frozen=True)
class Score:
    value: float
    maximum: float

    def __post_init__(self):
        if self.maximum <= 0:
            raise ValueError("Le maximum doit etre superieur à zéro")
        if self.value < 0:
            raise ValueError("La note ne peut pas etre négative")
        if self.value > self.maximum:
            raise ValueError("Note ne peut pas dépassé le maximum")

    def normalized_to_20(self) -> float:
        return (self.value / self.maximum) * 20
