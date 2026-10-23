from collections.abc import Iterable
import math

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

        try:
            total_coefficient = math.fsum(
                result.coefficient for result in subject_results
            )
            weighted_average = math.fsum(
                result.average * result.coefficient
                for result in subject_results
            )
            average = weighted_average / total_coefficient
        except OverflowError:
            total_coefficient = math.inf
            weighted_average = math.inf
            average = math.nan

        if (
            math.isfinite(total_coefficient)
            and math.isfinite(weighted_average)
            and math.isfinite(average)
        ):
            return average

        max_coefficient = max(result.coefficient for result in subject_results)
        scaled_coefficients = tuple(
            result.coefficient / max_coefficient for result in subject_results
        )
        total_coefficient = math.fsum(scaled_coefficients)
        weighted_average = math.fsum(
            result.average * coefficient
            for result, coefficient in zip(subject_results, scaled_coefficients)
        )
        return weighted_average / total_coefficient
