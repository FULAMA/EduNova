from dataclasses import dataclass

from tools.edunova.agents.evidence_assessment import EvidenceAssessment
from tools.edunova.agents.evidence_level import EvidenceLevel


@dataclass(frozen=True)
class EvidenceGateResult:
    admissible: bool
    requires_human_review: bool
    reason: str


class EvidenceGate:
    def evaluate(
        self,
        assessments: tuple[EvidenceAssessment, ...],
    ) -> EvidenceGateResult:
        if not assessments:
            return EvidenceGateResult(
                admissible=False,
                requires_human_review=True,
                reason="No evidence assessment is available.",
            )

        unknown = tuple(
            item
            for item in assessments
            if item.level is EvidenceLevel.UNKNOWN
        )

        non_observed = tuple(
            item
            for item in assessments
            if item.level is not EvidenceLevel.OBSERVED
        )

        if unknown:
            return EvidenceGateResult(
                admissible=False,
                requires_human_review=True,
                reason=(
                    "At least one required evidence item is UNKNOWN; "
                    "the available evidence is insufficient for a factual claim."
                ),
            )

        if non_observed:
            return EvidenceGateResult(
                admissible=False,
                requires_human_review=True,
                reason=(
                    "The evidence contains non-observed assessments "
                    "and cannot be treated as factual project evidence."
                ),
            )

        return EvidenceGateResult(
            admissible=True,
            requires_human_review=False,
            reason="All supplied evidence assessments are OBSERVED.",
        )
