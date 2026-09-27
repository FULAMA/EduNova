from src.academic.domain.entities.deliberation import (
    Deliberation,
    DeliberationDecision,
)
from src.academic.domain.policies.academic_policy import AcademicPolicy


class DeliberationEngine:

    def __init__(self, policy: AcademicPolicy):
        self.policy = policy

    def deliberate(
        self,
        student_id,
        average: float,
        failed_subjects: int,
    ) -> Deliberation:

        if self.policy.has_passing_average(average):
            decision = DeliberationDecision.ADMITTED

        elif self.policy.can_pass_with_failed_subjects(
            failed_subjects
        ):
            decision = DeliberationDecision.CONDITIONAL

        else:
            decision = DeliberationDecision.FAILED

        return Deliberation(
            student_id=student_id,
            average=average,
            failed_subjects=failed_subjects,
            decision=decision,
        )