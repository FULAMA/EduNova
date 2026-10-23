from dataclasses import dataclass

from tools.edunova.agents.architect import ArchitectureProposal
from tools.edunova.agents.inspector import InspectionResult
from tools.edunova.agents.reviewer import ReviewResult, ReviewStatus


@dataclass(frozen=True)
class AgentChainResult:
    inspection: InspectionResult
    architecture: ArchitectureProposal
    review: ReviewResult

    @property
    def success(self) -> bool:
        return self.review.status is ReviewStatus.APPROVED
