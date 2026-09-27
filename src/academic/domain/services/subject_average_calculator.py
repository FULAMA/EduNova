from collections.abc import Iterable

from src.academic.domain.entities.grade import Grade


class SubjectAverageCalculator:

    def calculate(self, grades: Iterable[Grade]) -> float:
        grades = list(grades)

        if not grades:
            raise ValueError(
                "Impossible de calculer une moyenne sans note."
            )

        total_weighted_score = 0.0
        total_coefficient = 0.0

        for grade in grades:
            normalized_score = grade.normalized_score()
            coefficient = grade.assessment.coefficient.value

            total_weighted_score += (
                normalized_score * coefficient
            )

            total_coefficient += coefficient

        if total_coefficient <= 0:
            raise ValueError(
                "La somme des coefficients doit être supérieure à zéro."
            )

        return total_weighted_score / total_coefficient