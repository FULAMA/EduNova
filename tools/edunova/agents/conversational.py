from pathlib import Path

from tools.edunova.agents.agent import Agent
from tools.edunova.agents.agent_chain import AgentChain
from tools.edunova.agents.context_analyzer import ContextAnalyzer
from tools.edunova.agents.evidence import TaskEvidenceCollector
from tools.edunova.agents.evidence_assessment import EvidenceAssessment
from tools.edunova.agents.evidence_assessor import EvidenceAssessor
from tools.edunova.agents.evidence_gate import EvidenceGate
from tools.edunova.agents.context_builder import ContextBuilder
from tools.edunova.agents.orchestration.service import AgentOrchestrationService
from tools.edunova.agents.prompt_builder import EngineeringPromptBuilder
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class ConversationalAgent(Agent):
    name = "assistant"
    role = AgentRole.BUILDER

    def __init__(
        self,
        service: AgentOrchestrationService,
        context_builder: ContextBuilder,
        context_analyzer: ContextAnalyzer,
        prompt_builder: EngineeringPromptBuilder,
        evidence_collector: TaskEvidenceCollector | None = None,
        evidence_assessor: EvidenceAssessor | None = None,
        evidence_gate: EvidenceGate | None = None,
        agent_chain: AgentChain | None = None,
    ) -> None:
        self._service = service
        self._context_builder = context_builder
        self._context_analyzer = context_analyzer
        self._prompt_builder = prompt_builder
        self._evidence_collector = (
            evidence_collector
            or TaskEvidenceCollector(Path.cwd())
        )
        self._evidence_assessor = (
            evidence_assessor
            or EvidenceAssessor()
        )
        self._evidence_gate = (
            evidence_gate
            or EvidenceGate()
        )
        self._agent_chain = agent_chain

    def run(self, task: str) -> AgentResult:
        if not task.strip():
            raise ValueError("Agent task cannot be empty.")

        context = self._context_builder.build()
        analysis = self._context_analyzer.analyze(context)
        engineering_context = self._prompt_builder.build(analysis)

        if self._agent_chain is not None:
            chain_result = self._agent_chain.run(
                task=task,
                context=context,
            )

            if not chain_result.success:
                return AgentResult(
                    agent=self.name,
                    role=self.role,
                    success=False,
                    message=(
                        "Agent chain blocked the task: "
                        f"{chain_result.review.status.value}"
                    ),
                    error="agent_chain_blocked",
                )

        evidence_section = ""
        evidence_assessments: tuple[EvidenceAssessment, ...] = ()

        if self._evidence_collector is not None:
            evidence = self._evidence_collector.collect(task)

            evidence_assessments = tuple(
                self._evidence_assessor.assess(
                    statement=(
                        f"Explicit evidence is available for {item.path}."
                    ),
                    evidence=item,
                )
                for item in evidence
            )

            evidence_section = (
                f"{self._evidence_collector.build_prompt_section(evidence)}\n\n"
                "STRUCTURED EVIDENCE ASSESSMENTS:\n"
            )

            if evidence_assessments:
                for assessment in evidence_assessments:
                    evidence_section += (
                        f"- level={assessment.level.value} "
                        f"statement={assessment.statement!r}"
                    )

                    if assessment.source_path is not None:
                        evidence_section += (
                            f" source={assessment.source_path!r}"
                        )

                    if (
                        assessment.start_line is not None
                        and assessment.end_line is not None
                    ):
                        evidence_section += (
                            f" lines={assessment.start_line}-"
                            f"{assessment.end_line}"
                        )

                    if assessment.reason:
                        evidence_section += (
                            f" reason={assessment.reason!r}"
                        )

                    evidence_section += "\n"
            else:
                evidence_section += "- none\n"

            if evidence_assessments:
                evidence_gate_result = self._evidence_gate.evaluate(
                    evidence_assessments
                )

                evidence_section += (
                    "EVIDENCE GATE:\n"
                    f"- admissible={evidence_gate_result.admissible}\n"
                    f"- requires_human_review="
                    f"{evidence_gate_result.requires_human_review}\n"
                    f"- reason={evidence_gate_result.reason!r}\n"
                )

                if evidence_gate_result.admissible:
                    evidence_section += (
                        "EVIDENCE POLICY:\n"
                        "- Supplied file evidence may be used for factual claims "
                        "within its explicit scope.\n"
                        "- Do not generalize file-scoped evidence to the whole project.\n"
                    )
                else:
                    evidence_section += (
                        "EVIDENCE POLICY:\n"
                        "- Evidence is not admissible as established project fact.\n"
                        "- Do not present UNKNOWN, HYPOTHESIS, or "
                        "RECOMMENDATION as observed facts.\n"
                        "- Do not infer missing implementation details.\n"
                        "- If the requested conclusion depends on unavailable "
                        "evidence, explicitly state that human verification is required.\n"
                    )

            evidence_section += "\n"

        enriched_task = (
            f"{engineering_context}\n\n"
            f"{evidence_section}"
            "ENGINEERING RULES:\n"
            "- Treat the engineering context as the only factual project evidence provided.\n"
            "- Do not invent files, modules, technologies, architecture, tests, decisions, or implementation details.\n"
            "- Do not claim that a component is missing, incomplete, broken, implemented, tested, or validated unless the context explicitly supports that claim.\n"
            "- Treat directory listings as evidence only that those directories were detected. Do not infer their internal contents or responsibilities.\n"
            "- Treat Git paths as evidence only for the exact paths and Git statuses shown. Do not infer the contents of those files.\n"
            "- Do not infer a technology, implementation, runtime behavior, dependency, database, framework, or architectural property from a file name, directory name, import name, or path alone.\n"
            "- Treat explicit file evidence as evidence about that exact file content only.\n"
            "- Do not generalize a fact observed in one file to the whole project unless another explicit evidence source establishes that project-wide fact.\n"
            "- A configuration value found in a file does not prove that the application currently uses that configuration at runtime.\n"
            "- A class, function, import, dependency, or implementation found in one file does not prove that it is instantiated, imported, executed, or used elsewhere.\n"
            "- A test file may prove what that test asserts or executes, but it does not by itself prove that the tested behavior is the complete current production behavior.\n"
            "- When evidence is file-scoped, state the scope explicitly instead of presenting the observation as a project-wide fact.\n"
            "- A file or test name such as test_sqlite_... is evidence only of that exact path name; it is never sufficient evidence that SQLite is the current database technology. For current technology claims, require explicit contextual evidence.\n"
            "- Do not describe the architecture as complete, correct, mature, clearly defined, or validated unless the context explicitly proves it.\n"
            "- Do not transform the existence of directories into claims about modules, layers, responsibilities, dependencies, or design quality.\n"
            "- Do not transform the existence of tests into claims about test coverage, robustness, correctness, or passing status.\n"
            "- Do not transform a modified file into a claim about what was implemented, fixed, added, removed, or reviewed inside that file.\n"
            "- When the context does not contain enough evidence, explicitly state that the information is unknown.\n"
            "- Distinguish clearly between observed facts, reasonable hypotheses, and recommendations.\n"
            "- Before identifying a technical risk, verify that the context contains evidence for it.\n"
            "- Do not silently import assumptions from other projects or generic software architectures.\n"
            "- Classify statements by evidence level: OBSERVED, UNKNOWN, HYPOTHESIS, or RECOMMENDATION.\n"
            "- OBSERVED means the statement is directly supported by explicit project evidence available in the context.\n"
            "- UNKNOWN means the available evidence is insufficient to establish the statement as a fact.\n"
            "- HYPOTHESIS means a possible explanation that is not established by direct evidence; label it explicitly as a hypothesis.\n"
            "- RECOMMENDATION means proposed action or guidance, not an observed project fact.\n"
            "- Never present a HYPOTHESIS or RECOMMENDATION as OBSERVED.\n"
            "- When answering factual questions about the project, prefer OBSERVED or UNKNOWN over unsupported inference.\n"
            "USER TASK:\n"
            f"{task}"
        )

        result = self._service.run(enriched_task)

        return AgentResult(
            agent=self.name,
            role=self.role,
            success=result.success,
            message=result.message,
            provider=result.provider,
            model=result.model,
            duration_ms=result.duration_ms,
            error=result.error,
        )
