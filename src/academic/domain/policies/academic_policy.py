from dataclasses import dataclass


@dataclass(frozen=True)
class AcademicPolicy:
    grading_scale: float = 20.0
    passing_average: float = 10.0
    minimum_subject_average: float = 8.0
    max_failed_subjects: int = 2
    rounding_precision: int = 2

    def __post_init__(self):
        if self.grading_scale <= 0:
            raise ValueError(
                "L'échelle de notation doit être positive."
            )

        if not 0 <= self.passing_average <= self.grading_scale:
            raise ValueError(
                "La moyenne de passage est invalide."
            )

        if not 0 <= self.minimum_subject_average <= self.grading_scale:
            raise ValueError(
                "Le seuil matière est invalide."
            )

        if self.max_failed_subjects < 0:
            raise ValueError(
                "Le nombre de matières échouées est invalide."
            )

        if self.rounding_precision < 0:
            raise ValueError(
                "La précision d'arrondi est invalide."
            )

    def has_passing_average(self, average: float) -> bool:
        return average >= self.passing_average

    def is_subject_passed(self, average: float) -> bool:
        return average >= self.minimum_subject_average

    def can_pass_with_failed_subjects(
        self,
        failed_subjects: int,
    ) -> bool:
        return failed_subjects <= self.max_failed_subjects

    def round_average(self, average: float) -> float:
        return round(
            average,
            self.rounding_precision,
        )