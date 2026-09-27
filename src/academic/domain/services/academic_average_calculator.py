from collections.abc import Iterable

from src.academic.domain.value_objects.subject_result import SubjectResult


class AcademicAverageCalculator:

    def calculate(
        self,
        subject_results: Iterable[SubjectResult],
    ) -> float:

        subject_results = list(subject_results)

        if not subject_results:
            raise ValueError(
                "Impossible de calculer une moyenne gÃ©nÃ©rale "
                "sans rÃ©sultat de matiÃ¨re."
            )

        total_weighted_average = 0.0
        total_coefficient = 0.0

        for result in subject_results:
            total_weighted_average += (
                result.average * result.coefficient
            )

            total_coefficient += result.coefficient

        if total_coefficient <= 0:
            raise ValueError(
                "La somme des coefficients doit Ãªtre supÃ©rieure Ã  zÃ©ro."
            )

        return total_weighted_average / total_coefficient
