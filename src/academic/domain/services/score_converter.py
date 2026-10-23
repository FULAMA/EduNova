from typing import Protocol

from src.academic.domain.value_objects.score import Score


class ScoreConverter(Protocol):
    def convert(self, score: Score) -> float:
        ...


class Scale20Converter:
    """
    Convertisseur compatible avec la règle historique /20.

    Cette implémentation conserve temporairement la logique existante
    de Score.normalized_to_20().
    """

    def convert(self, score: Score) -> float:
        return score.normalized_to_20()
