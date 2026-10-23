from dataclasses import dataclass

import pytest

from tools.edunova.agents.agent_chain import AgentChain
from tools.edunova.agents.architect import Architect
from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import ContextAnalyzer
from tools.edunova.agents.inspector import Inspector
from tools.edunova.agents.reviewer import ReviewStatus, Reviewer


@dataclass
class StubContextAnalyzer:
    calls: int = 0

    def analyze(self, context: EngineeringContext):
        self.calls += 1
        return ContextAnalyzer().analyze(context)


class StubInspector(Inspector):
    def __init__(self) -> None:
        self.calls = 0

    def inspect(self, context, analysis):
        self.calls += 1
        return super().inspect(context, analysis)


class StubArchitect(Architect):
    def __init__(self) -> None:
        self.calls = 0

    def propose(self, task, context, inspection):
        self.calls += 1
        return super().propose(task, context, inspection)


class StubReviewer(Reviewer):
    def __init__(self) -> None:
        self.calls = 0

    def review(self, proposal):
        self.calls += 1
        return super().review(proposal)


def make_context() -> EngineeringContext:
    return EngineeringContext(
        project_root=__import__("pathlib").Path("."),
        scope="test",
    )


def make_chain():
    context_analyzer = StubContextAnalyzer()
    inspector = StubInspector()
    architect = StubArchitect()
    reviewer = StubReviewer()

    chain = AgentChain(
        inspector=inspector,
        architect=architect,
        reviewer=reviewer,
        context_analyzer=context_analyzer,
    )

    return chain, context_analyzer, inspector, architect, reviewer


def test_agent_chain_runs_inspector_architect_reviewer_in_order():
    chain, context_analyzer, inspector, architect, reviewer = make_chain()

    result = chain.run(
        "inspect academic records",
        make_context(),
    )

    assert result.success is True
    assert result.review.status is ReviewStatus.APPROVED

    assert context_analyzer.calls == 1
    assert inspector.calls == 1
    assert architect.calls == 1
    assert reviewer.calls == 1

    assert result.architecture.task == "inspect academic records"


def test_agent_chain_rejects_empty_task():
    chain, *_ = make_chain()

    with pytest.raises(ValueError, match="empty"):
        chain.run("   ", make_context())


def test_agent_chain_produces_architecture_from_inspection():
    chain, _, inspector, architect, reviewer = make_chain()

    result = chain.run(
        "design academic records",
        make_context(),
    )

    assert inspector.calls == 1
    assert architect.calls == 1
    assert reviewer.calls == 1

    assert result.inspection.read_only is True
    assert result.architecture.read_only is True
    assert result.architecture.task == "design academic records"


def test_agent_chain_returns_changes_required_when_human_decision_is_needed():
    class HumanReviewContextAnalyzer:
        def analyze(self, context):
            from tools.edunova.agents.context_analyzer import EngineeringAnalysis

            return EngineeringAnalysis(
                scope="test",
                git_branch="",
                changed_files=(),
                architecture=(),
                tests=(),
                decisions=(),
                risks=(),
                is_clean=True,
            )

    class HumanReviewInspector(Inspector):
        def inspect(self, context, analysis):
            from tools.edunova.agents.inspector import InspectionResult

            return InspectionResult(
                scope=analysis.scope,
                changed_file_count=0,
                risks=(),
                requires_human_review=True,
                affected_files=(),
                read_only=True,
            )

    chain = AgentChain(
        inspector=HumanReviewInspector(),
        architect=Architect(),
        reviewer=Reviewer(),
        context_analyzer=HumanReviewContextAnalyzer(),
    )

    result = chain.run(
        "change architecture",
        make_context(),
    )

    assert result.review.status is ReviewStatus.CHANGES_REQUIRED
    assert result.success is False


def test_agent_chain_blocks_when_architecture_has_risks():
    class RiskyInspector(Inspector):
        def inspect(self, context, analysis):
            from tools.edunova.agents.inspector import InspectionResult

            return InspectionResult(
                scope=analysis.scope,
                changed_file_count=0,
                risks=("unverified risk",),
                requires_human_review=True,
                affected_files=(),
                read_only=True,
            )

    chain = AgentChain(
        inspector=RiskyInspector(),
        architect=Architect(),
        reviewer=Reviewer(),
        context_analyzer=ContextAnalyzer(),
    )

    result = chain.run(
        "change architecture",
        make_context(),
    )

    assert result.review.status is ReviewStatus.BLOCKED
    assert result.success is False
