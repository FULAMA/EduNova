from tools.edunova.agents.architect import Architect
from tools.edunova.agents.chain_result import AgentChainResult
from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import ContextAnalyzer
from tools.edunova.agents.inspector import Inspector
from tools.edunova.agents.reviewer import Reviewer


class AgentChain:
    def __init__(
        self,
        inspector: Inspector,
        architect: Architect,
        reviewer: Reviewer,
        context_analyzer: ContextAnalyzer,
    ) -> None:
        self._inspector = inspector
        self._architect = architect
        self._reviewer = reviewer
        self._context_analyzer = context_analyzer

    def run(
        self,
        task: str,
        context: EngineeringContext,
    ) -> AgentChainResult:
        if not task.strip():
            raise ValueError("Agent chain task cannot be empty.")

        analysis = self._context_analyzer.analyze(context)

        inspection = self._inspector.inspect(
            context=context,
            analysis=analysis,
        )

        architecture = self._architect.propose(
            task=task,
            context=context,
            inspection=inspection,
        )

        review = self._reviewer.review(architecture)

        return AgentChainResult(
            inspection=inspection,
            architecture=architecture,
            review=review,
        )
