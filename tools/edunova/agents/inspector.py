from dataclasses import dataclass

from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import EngineeringAnalysis


@dataclass(frozen=True)
class InspectionResult:
    scope: str
    changed_file_count: int
    risks: tuple[str, ...]
    requires_human_review: bool
    affected_files: tuple[str, ...]
    read_only: bool


class Inspector:
    def inspect(
        self,
        context: EngineeringContext,
        analysis: EngineeringAnalysis,
    ) -> InspectionResult:
        return InspectionResult(
            scope=analysis.scope,
            changed_file_count=analysis.changed_file_count,
            risks=analysis.risks,
            requires_human_review=bool(analysis.risks),
            affected_files=analysis.changed_files,
            read_only=True,
        )
