from pathlib import Path

from tools.edunova.agents.agent_chain import AgentChain
from tools.edunova.agents.architect import Architect
from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import ContextAnalyzer
from tools.edunova.agents.context_builder import ContextBuilder
from tools.edunova.agents.conversational import ConversationalAgent
from tools.edunova.agents.inspector import Inspector
from tools.edunova.agents.prompt_builder import EngineeringPromptBuilder
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.reviewer import Reviewer
from tools.edunova.agents.role import AgentRole


class ChainScanner:
    def build_context(self):
        return EngineeringContext(
            project_root=Path("F:/EduNova"),
            scope="chain-test",
        )


class RecordingService:
    def __init__(self):
        self.calls = 0
        self.received_task = None

    def run(self, task):
        self.calls += 1
        self.received_task = task

        return AgentResult(
            agent="groq",
            role=AgentRole.BUILDER,
            success=True,
            message="provider executed",
            provider="groq",
            model="test-model",
        )


class RecordingChain:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def run(self, task, context):
        self.calls += 1
        return self.result


def make_context():
    return EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="chain-test",
    )


def make_agent(service, chain):
    class Scanner:
        def scan(self):
            return make_context()

    return ConversationalAgent(
        service=service,
        context_builder=ContextBuilder(Scanner()),
        context_analyzer=ContextAnalyzer(),
        prompt_builder=EngineeringPromptBuilder(),
        agent_chain=chain,
    )


def make_approved_chain():
    return AgentChain(
        inspector=Inspector(),
        architect=Architect(),
        reviewer=Reviewer(),
        context_analyzer=ContextAnalyzer(),
    )


def test_conversational_agent_runs_agent_chain_before_provider():
    service = RecordingService()
    chain = RecordingChain(
        make_approved_chain().run(
            "analyse project",
            make_context(),
        )
    )

    agent = make_agent(service, chain)

    result = agent.run("analyse project")

    assert result.success is True
    assert chain.calls == 1
    assert service.calls == 1


def test_conversational_agent_does_not_call_provider_when_chain_is_blocked():
    from tools.edunova.agents.agent_chain import AgentChainResult
    from tools.edunova.agents.inspector import InspectionResult
    from tools.edunova.agents.architect import ArchitectureProposal
    from tools.edunova.agents.reviewer import ReviewResult, ReviewStatus

    blocked = AgentChainResult(
        inspection=InspectionResult(
            scope="test",
            changed_file_count=0,
            risks=("unverified risk",),
            requires_human_review=True,
            affected_files=(),
            read_only=True,
        ),
        architecture=ArchitectureProposal(
            task="change architecture",
            scope="test",
            affected_files=(),
            risks=("unverified risk",),
            requires_human_decision=True,
            read_only=True,
        ),
        review=ReviewResult(
            task="change architecture",
            status=ReviewStatus.BLOCKED,
            affected_files=(),
            read_only=True,
        ),
    )

    service = RecordingService()
    chain = RecordingChain(blocked)

    agent = make_agent(service, chain)

    result = agent.run("change architecture")

    assert result.success is False
    assert result.error == "agent_chain_blocked"
    assert "BLOCKED" in result.message
    assert chain.calls == 1
    assert service.calls == 0
