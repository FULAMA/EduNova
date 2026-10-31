from pathlib import Path

from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import ContextAnalyzer
from tools.edunova.agents.context_builder import ContextBuilder
from tools.edunova.agents.conversational import ConversationalAgent
from tools.edunova.agents.evidence import TaskEvidenceCollector
from tools.edunova.agents.evidence_assessor import EvidenceAssessor
from tools.edunova.agents.evidence_gate import EvidenceGate
from tools.edunova.agents.prompt_builder import EngineeringPromptBuilder
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeOrchestrationService:
    def __init__(self):
        self.received_task = None

    def run(self, task):
        self.received_task = task

        return AgentResult(
            agent="groq",
            role=AgentRole.BUILDER,
            success=True,
            message="Réponse simulée.",
            provider="groq",
            model="openai/gpt-oss-20b",
        )


class FakeScanner:
    def __init__(self):
        self.calls = 0

    def scan(self):
        self.calls += 1

        return EngineeringContext(
            project_root=Path("F:/EduNova"),
            scope="test-agent",
            git_branch="main",
            git_status=(),
            changed_files=("src/academic/example.py",),
            architecture=("src/academic", "src/identity"),
            tests=("tests/unit",),
            decisions=(),
            risks=(),
        )


def make_agent(service):
    scanner = FakeScanner()

    return (
        ConversationalAgent(
            service=service,
            context_builder=ContextBuilder(scanner),
            context_analyzer=ContextAnalyzer(),
            prompt_builder=EngineeringPromptBuilder(),
        ),
        scanner,
    )


def test_conversational_agent_enriches_question_with_engineering_context():
    service = FakeOrchestrationService()
    agent, scanner = make_agent(service)

    result = agent.run("Analyse le problème actuel.")

    assert scanner.calls == 1
    assert service.received_task is not None

    assert "EDUNOVA ENGINEERING CONTEXT" in service.received_task
    assert "Scope: test-agent" in service.received_task
    assert "Git branch: main" in service.received_task
    assert "src/academic/example.py" in service.received_task
    assert "src/academic" in service.received_task
    assert "tests/unit" in service.received_task

    assert "ENGINEERING RULES:" in service.received_task
    assert "Do not invent files" in service.received_task
    assert "information is unknown" in service.received_task
    assert "USER TASK:" in service.received_task
    assert "Analyse le problème actuel." in service.received_task

    assert result.success is True
    assert result.agent == "assistant"
    assert result.role == AgentRole.BUILDER
    assert result.message == "Réponse simulée."
    assert result.provider == "groq"


def test_conversational_agent_does_not_invent_architecture():
    service = FakeOrchestrationService()
    agent, _ = make_agent(service)

    agent.run("Analyse le projet.")

    assert "tenant_id" not in service.received_task
    assert "PostgreSQL" not in service.received_task
    assert "StudentAcademicRecord" not in service.received_task


def test_conversational_agent_includes_anti_hallucination_rules():
    service = FakeOrchestrationService()
    agent, _ = make_agent(service)

    agent.run("Analyse le projet.")

    prompt = service.received_task

    assert "Treat the engineering context as the only factual project evidence provided." in prompt
    assert "Distinguish clearly between observed facts, reasonable hypotheses, and recommendations." in prompt
    assert "Before identifying a technical risk, verify that the context contains evidence for it." in prompt


def test_conversational_agent_rejects_empty_task():
    service = FakeOrchestrationService()
    agent, scanner = make_agent(service)

    try:
        agent.run("")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")

    assert scanner.calls == 0
    assert service.received_task is None


def test_agent_forbids_database_inference_from_sqlite_test_name():
    service = FakeOrchestrationService()

    agent, _ = make_agent(service)

    agent.run("Quelle est la technologie de base de données actuellement utilisée ?")

    prompt = service.received_task

    assert "test_sqlite_..." in prompt
    assert "never sufficient evidence that SQLite is the current database technology" in prompt
    assert "require explicit contextual evidence" in prompt

def test_agent_includes_explicit_file_evidence():
    service = FakeOrchestrationService()

    scanner = FakeScanner()

    context_builder = ContextBuilder(scanner)
    context_analyzer = ContextAnalyzer()
    prompt_builder = EngineeringPromptBuilder()

    collector = TaskEvidenceCollector(Path.cwd())

    agent = ConversationalAgent(
        service=service,
        context_builder=context_builder,
        context_analyzer=context_analyzer,
        prompt_builder=prompt_builder,
        evidence_collector=collector,
    )

    agent.run("Analyse tools/edunova/agents/evidence.py")

    prompt = service.received_task

    assert "EXPLICIT FILE EVIDENCE:" in prompt
    assert "FILE: tools/edunova/agents/evidence.py" in prompt
    assert "class TaskEvidenceCollector" in prompt

def test_agent_forbids_inference_from_file_names_or_paths():
    service = FakeOrchestrationService()

    agent, _ = make_agent(service)

    agent.run("Analyse la technologie de base de données actuellement utilisée.")

    prompt = service.received_task

    assert "Do not infer a technology, implementation, runtime behavior" in prompt
    assert "from a file name, directory name, import name, or path alone" in prompt
def test_agent_forbids_semantic_inference_from_directory_and_git_evidence():
    service = FakeOrchestrationService()

    agent, _ = make_agent(service)

    agent.run("Analyse le projet.")

    prompt = service.received_task

    assert "Do not transform the existence of directories into claims about modules" in prompt
    assert "Do not transform the existence of tests into claims about test coverage" in prompt
    assert "Do not transform a modified file into a claim about what was implemented" in prompt
    assert "Do not describe the architecture as complete, correct, mature" in prompt



def test_prompt_limits_explicit_file_evidence_to_that_file():
    source = Path(
        "tools/edunova/agents/conversational.py"
    )

    text = source.read_text(encoding="utf-8")

    assert "Treat explicit file evidence as evidence about that exact file content only." in text
    assert "Do not generalize a fact observed in one file to the whole project" in text
    assert "A configuration value found in a file does not prove that the application currently uses that configuration at runtime." in text
    assert "A class, function, import, dependency, or implementation found in one file does not prove that it is instantiated, imported, executed, or used elsewhere." in text

def test_agent_includes_structured_observed_evidence():
    service = FakeOrchestrationService()

    scanner = FakeScanner()

    agent = ConversationalAgent(
        service=service,
        context_builder=ContextBuilder(scanner),
        context_analyzer=ContextAnalyzer(),
        prompt_builder=EngineeringPromptBuilder(),
        evidence_collector=TaskEvidenceCollector(Path.cwd()),
        evidence_assessor=EvidenceAssessor(),
    )

    agent.run("Analyse tools/edunova/agents/evidence.py")

    prompt = service.received_task

    assert "STRUCTURED EVIDENCE ASSESSMENTS:" in prompt
    assert "level=observed" in prompt
    assert "source='tools/edunova/agents/evidence.py'" in prompt
    assert "lines=" in prompt


def test_agent_does_not_mark_unreferenced_files_as_structured_evidence():
    service = FakeOrchestrationService()

    agent, _ = make_agent(service)

    agent.run("Analyse le projet sans référencer de fichier.")

    prompt = service.received_task

    assert "STRUCTURED EVIDENCE ASSESSMENTS:" in prompt
    assert "STRUCTURED EVIDENCE ASSESSMENTS:\n- none" in prompt


def test_agent_structured_evidence_preserves_unknown_level_for_missing_file():
    service = FakeOrchestrationService()

    scanner = FakeScanner()

    collector = TaskEvidenceCollector(Path.cwd())

    agent = ConversationalAgent(
        service=service,
        context_builder=ContextBuilder(scanner),
        context_analyzer=ContextAnalyzer(),
        prompt_builder=EngineeringPromptBuilder(),
        evidence_collector=collector,
        evidence_assessor=EvidenceAssessor(),
    )

    agent.run("Analyse src/this_file_does_not_exist.py")

    prompt = service.received_task

    assert "STRUCTURED EVIDENCE ASSESSMENTS:" in prompt
    assert "level=unknown" in prompt
    assert "source=" not in prompt


def test_agent_accepts_injected_evidence_assessor():
    service = FakeOrchestrationService()

    class SpyAssessor(EvidenceAssessor):
        def __init__(self):
            self.calls = 0

        def assess(self, statement, evidence):
            self.calls += 1
            return super().assess(statement, evidence)

    assessor = SpyAssessor()

    scanner = FakeScanner()

    agent = ConversationalAgent(
        service=service,
        context_builder=ContextBuilder(scanner),
        context_analyzer=ContextAnalyzer(),
        prompt_builder=EngineeringPromptBuilder(),
        evidence_collector=TaskEvidenceCollector(Path.cwd()),
        evidence_assessor=assessor,
    )

    agent.run("Analyse tools/edunova/agents/evidence.py")

    assert assessor.calls == 1


def test_agent_includes_evidence_gate_result():
    class StubContextBuilder:
        def build(self):
            return object()

    class StubContextAnalyzer:
        def analyze(self, context):
            return type(
                "Analysis",
                (),
                {
                    "scope": "test",
                    "git_branch": "",
                    "git_changes": (),
                    "changed_files": (),
                    "architecture": (),
                    "tests": (),
                    "decisions": (),
                    "risks": (),
                    "is_clean": True,
                },
            )()

    class StubPromptBuilder:
        def build(self, analysis):
            return "ENGINEERING CONTEXT"

    class StubEvidenceCollector:
        def collect(self, task):
            from tools.edunova.agents.evidence import EvidenceItem

            return (
                EvidenceItem(
                    path="src/example.py",
                    exists=True,
                    content="value = 1\n",
                    start_line=1,
                    end_line=1,
                ),
            )

        def build_prompt_section(self, evidence):
            return "EXPLICIT FILE EVIDENCE:\n"

    class StubService:
        def run(self, task):
            from tools.edunova.agents.result import AgentResult
            from tools.edunova.agents.role import AgentRole

            assert "EVIDENCE GATE:" in task
            assert "admissible=True" in task
            assert "requires_human_review=False" in task

            return AgentResult(
                agent="stub",
                role=AgentRole.BUILDER,
                success=True,
                message="ok",
            )

    agent = ConversationalAgent(
        service=StubService(),
        context_builder=StubContextBuilder(),
        context_analyzer=StubContextAnalyzer(),
        prompt_builder=StubPromptBuilder(),
        evidence_collector=StubEvidenceCollector(),
        evidence_assessor=EvidenceAssessor(),
        evidence_gate=EvidenceGate(),
    )

    result = agent.run("Inspect src/example.py")

    assert result.success is True


def test_agent_marks_unknown_evidence_as_human_review():
    class StubContextBuilder:
        def build(self):
            return object()

    class StubContextAnalyzer:
        def analyze(self, context):
            return type(
                "Analysis",
                (),
                {
                    "scope": "test",
                    "git_branch": "",
                    "git_changes": (),
                    "changed_files": (),
                    "architecture": (),
                    "tests": (),
                    "decisions": (),
                    "risks": (),
                    "is_clean": True,
                },
            )()

    class StubPromptBuilder:
        def build(self, analysis):
            return "ENGINEERING CONTEXT"

    class StubEvidenceCollector:
        def collect(self, task):
            from tools.edunova.agents.evidence import EvidenceItem

            return (
                EvidenceItem(
                    path="src/missing.py",
                    exists=False,
                ),
            )

        def build_prompt_section(self, evidence):
            return "EXPLICIT FILE EVIDENCE:\n"

    class StubService:
        def run(self, task):
            from tools.edunova.agents.result import AgentResult
            from tools.edunova.agents.role import AgentRole

            assert "EVIDENCE GATE:" in task
            assert "admissible=False" in task
            assert "requires_human_review=True" in task

            return AgentResult(
                agent="stub",
                role=AgentRole.BUILDER,
                success=True,
                message="ok",
            )

    agent = ConversationalAgent(
        service=StubService(),
        context_builder=StubContextBuilder(),
        context_analyzer=StubContextAnalyzer(),
        prompt_builder=StubPromptBuilder(),
        evidence_collector=StubEvidenceCollector(),
        evidence_assessor=EvidenceAssessor(),
        evidence_gate=EvidenceGate(),
    )

    result = agent.run("Inspect src/missing.py")

    assert result.success is True

def test_agent_applies_admissible_evidence_policy():
    class StubContextBuilder:
        def build(self):
            return object()

    class StubContextAnalyzer:
        def analyze(self, context):
            return type(
                "Analysis",
                (),
                {
                    "scope": "test",
                    "git_branch": "",
                    "git_changes": (),
                    "changed_files": (),
                    "architecture": (),
                    "tests": (),
                    "decisions": (),
                    "risks": (),
                    "is_clean": True,
                },
            )()

    class StubPromptBuilder:
        def build(self, analysis):
            return "ENGINEERING CONTEXT"

    class StubEvidenceCollector:
        def collect(self, task):
            from tools.edunova.agents.evidence import EvidenceItem

            return (
                EvidenceItem(
                    path="src/example.py",
                    exists=True,
                    content="value = 1\n",
                    start_line=1,
                    end_line=1,
                ),
            )

        def build_prompt_section(self, evidence):
            return "EXPLICIT FILE EVIDENCE:\n"

    class StubService:
        def run(self, task):
            from tools.edunova.agents.result import AgentResult
            from tools.edunova.agents.role import AgentRole

            assert "EVIDENCE POLICY:" in task
            assert "Supplied file evidence may be used" in task
            assert "Do not generalize file-scoped evidence" in task

            return AgentResult(
                agent="stub",
                role=AgentRole.BUILDER,
                success=True,
                message="ok",
            )

    agent = ConversationalAgent(
        service=StubService(),
        context_builder=StubContextBuilder(),
        context_analyzer=StubContextAnalyzer(),
        prompt_builder=StubPromptBuilder(),
        evidence_collector=StubEvidenceCollector(),
        evidence_assessor=EvidenceAssessor(),
        evidence_gate=EvidenceGate(),
    )

    result = agent.run("Inspect src/example.py")

    assert result.success is True


def test_agent_applies_review_policy_for_unknown_evidence():
    class StubContextBuilder:
        def build(self):
            return object()

    class StubContextAnalyzer:
        def analyze(self, context):
            return type(
                "Analysis",
                (),
                {
                    "scope": "test",
                    "git_branch": "",
                    "git_changes": (),
                    "architecture": (),
                    "tests": (),
                    "decisions": (),
                    "risks": (),
                    "is_clean": True,
                },
            )()

    class StubPromptBuilder:
        def build(self, analysis):
            return "ENGINEERING CONTEXT"

    class StubEvidenceCollector:
        def collect(self, task):
            from tools.edunova.agents.evidence import EvidenceItem

            return (
                EvidenceItem(
                    path="src/missing.py",
                    exists=False,
                ),
            )

        def build_prompt_section(self, evidence):
            return "EXPLICIT FILE EVIDENCE:\n"

    class StubService:
        def run(self, task):
            from tools.edunova.agents.result import AgentResult
            from tools.edunova.agents.role import AgentRole

            assert "EVIDENCE POLICY:" in task
            assert "Evidence is not admissible as established project fact." in task
            assert "human verification is required" in task
            assert "Do not infer missing implementation details." in task

            return AgentResult(
                agent="stub",
                role=AgentRole.BUILDER,
                success=True,
                message="ok",
            )

    agent = ConversationalAgent(
        service=StubService(),
        context_builder=StubContextBuilder(),
        context_analyzer=StubContextAnalyzer(),
        prompt_builder=StubPromptBuilder(),
        evidence_collector=StubEvidenceCollector(),
        evidence_assessor=EvidenceAssessor(),
        evidence_gate=EvidenceGate(),
    )

    result = agent.run("Inspect src/missing.py")

    assert result.success is True
