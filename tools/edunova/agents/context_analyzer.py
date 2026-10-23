from dataclasses import dataclass

from tools.edunova.agents.context import EngineeringContext, GitChange


@dataclass(frozen=True)
class EngineeringAnalysis:
    scope: str
    git_branch: str
    changed_files: tuple[str, ...]
    architecture: tuple[str, ...]
    tests: tuple[str, ...]
    decisions: tuple[str, ...]
    risks: tuple[str, ...]
    is_clean: bool
    git_changes: tuple[GitChange, ...] = ()

    @property
    def changed_file_count(self) -> int:
        return len(self.changed_files)


class ContextAnalyzer:
    def analyze(
        self,
        context: EngineeringContext,
    ) -> EngineeringAnalysis:
        return EngineeringAnalysis(
            scope=context.scope,
            git_branch=context.git_branch,
            changed_files=context.changed_files,
            architecture=context.architecture,
            tests=context.tests,
            decisions=context.decisions,
            risks=context.risks,
            is_clean=not context.changed_files and not context.risks,
            git_changes=context.git_changes,
        )
