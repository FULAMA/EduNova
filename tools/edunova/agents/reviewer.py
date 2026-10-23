from dataclasses import dataclass
from enum import Enum

from tools.edunova.agents.architect import ArchitectureProposal


class ReviewStatus(str, Enum):
    APPROVED = "APPROVED"
    CHANGES_REQUIRED = "CHANGES_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ReviewResult:
    task: str
    status: ReviewStatus
    affected_files: tuple[str, ...]
    read_only: bool


class Reviewer:
    def review(self, proposal: ArchitectureProposal) -> ReviewResult:
        if not proposal.task.strip():
            status = ReviewStatus.BLOCKED
        elif not proposal.read_only:
            status = ReviewStatus.BLOCKED
        elif proposal.risks:
            status = ReviewStatus.BLOCKED
        elif proposal.requires_human_decision:
            status = ReviewStatus.CHANGES_REQUIRED
        else:
            status = ReviewStatus.APPROVED

        return ReviewResult(
            task=proposal.task,
            status=status,
            affected_files=proposal.affected_files,
            read_only=True,
        )
