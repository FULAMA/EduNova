from tools.edunova.agents.evidence import EvidenceItem
from tools.edunova.agents.evidence_assessment import EvidenceAssessment
from tools.edunova.agents.evidence_level import EvidenceLevel


class EvidenceAssessor:
    def assess(
        self,
        statement: str,
        evidence: EvidenceItem,
    ) -> EvidenceAssessment:
        if (
            evidence.exists
            and evidence.start_line is not None
            and evidence.end_line is not None
            and not evidence.content.startswith("[CONTENT OMITTED:")
            and not evidence.content.startswith("[CONTENT UNAVAILABLE:")
        ):
            return EvidenceAssessment(
                statement=statement,
                level=EvidenceLevel.OBSERVED,
                source_path=evidence.path,
                start_line=evidence.start_line,
                end_line=evidence.end_line,
                reason="The statement is supported by directly read file content.",
            )

        if evidence.exists:
            return EvidenceAssessment(
                statement=statement,
                level=EvidenceLevel.UNKNOWN,
                reason=(
                    "The file was identified, but its complete content "
                    "was not directly available as evidence."
                ),
            )

        return EvidenceAssessment(
            statement=statement,
            level=EvidenceLevel.UNKNOWN,
            reason="The referenced file does not exist.",
        )
