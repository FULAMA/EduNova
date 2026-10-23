from dataclasses import dataclass

from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.inspector import InspectionResult


@dataclass(frozen=True)
class ArchitectureProposal:
    task: str
    scope: str
    affected_files: tuple[str, ...]
    risks: tuple[str, ...]
    requires_human_decision: bool
    read_only: bool


class Architect:
    def propose(
        self,
        task: str,
        context: EngineeringContext,
        inspection: InspectionResult,
    ) -> ArchitectureProposal:
        if not task.strip():
            raise ValueError("Task cannot be empty.")

        return ArchitectureProposal(
            task=task,
            scope=inspection.scope,
            affected_files=inspection.affected_files,
            risks=inspection.risks,
            requires_human_decision=inspection.requires_human_review,
            read_only=True,
        )
