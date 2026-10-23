from pathlib import Path

from tools.edunova.agents.agent_chain import AgentChain
from tools.edunova.agents.architect import Architect
from tools.edunova.agents.context_analyzer import ContextAnalyzer
from tools.edunova.agents.context_builder import ContextBuilder
from tools.edunova.agents.context_scanner import ContextScanner
from tools.edunova.agents.conversational import ConversationalAgent
from tools.edunova.agents.inspector import Inspector
from tools.edunova.agents.orchestration.service import (
    AgentOrchestrationService,
)
from tools.edunova.agents.prompt_builder import EngineeringPromptBuilder
from tools.edunova.agents.reviewer import Reviewer
from tools.edunova.commands.agent import (
    AgentCommand,
    OrchestratedAgentCommand,
)
from tools.edunova.commands.diagnose import DiagnoseCommand
from tools.edunova.commands.quality import QualityCommand
from tools.edunova.commands.run_tests import RunTestsCommand
from tools.edunova.commands.security import SecurityCommand
from tools.edunova.commands.work import WorkCommand
from tools.edunova.core.command_registry import CommandRegistry
from tools.edunova.core.command_service import CommandService
from tools.edunova.core.dispatcher import CommandDispatcher
from tools.edunova.core.runner import CommandRunner
from tools.edunova.extensions.fulama_workflow import FulamaWorkflow
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig


class CliBootstrap:
    def __init__(
        self,
        process_runner: ProcessRunner | None = None,
        agent_service: AgentOrchestrationService | None = None,
        project_config: ProjectConfig | None = None,
        audit_sink: ExecutionAuditSink | None = None,
    ) -> None:
        self._registry = CommandRegistry()
        self._runner = CommandRunner()
        self._project_config = project_config or ProjectConfig.load()
        self._process_runner = process_runner or ProcessRunner(
            timeout=self._project_config.timeout_seconds
        )
        self._agent_service = agent_service
        self._audit_sink = audit_sink

        self._register_commands()

        self._service = CommandService(
            registry=self._registry,
            runner=self._runner,
        )
        self._dispatcher = CommandDispatcher(self._service)

    @property
    def registry(self) -> CommandRegistry:
        return self._registry

    @property
    def runner(self) -> CommandRunner:
        return self._runner

    @property
    def service(self) -> CommandService:
        return self._service

    @property
    def dispatcher(self) -> CommandDispatcher:
        return self._dispatcher

    def _register_commands(self) -> None:
        run_tests = RunTestsCommand(
            self._process_runner,
            self._project_config,
            self._audit_sink,
        )
        quality = QualityCommand(
            self._process_runner,
            self._project_config,
            audit_sink=self._audit_sink,
        )
        security = SecurityCommand(
            self._process_runner,
            self._project_config,
            self._audit_sink,
        )

        self._registry.register(run_tests)
        self._registry.register(quality)
        self._registry.register(security)
        self._registry.register(
            DiagnoseCommand(
                self._process_runner,
                self._project_config,
                audit_sink=self._audit_sink,
            )
        )

        self._registry.register(
            WorkCommand([quality, security])
        )
        FulamaWorkflow.register(
            self._registry,
            [quality, security],
        )

        if self._agent_service is not None:
            project_root = Path.cwd()

            scanner = ContextScanner(
                project_root=project_root,
                scope="cli-agent",
                process_runner=self._process_runner,
                audit_sink=self._audit_sink,
            )

            context_builder = ContextBuilder(scanner)
            context_analyzer = ContextAnalyzer()
            prompt_builder = EngineeringPromptBuilder()

            agent_chain = AgentChain(
                inspector=Inspector(),
                architect=Architect(),
                reviewer=Reviewer(),
                context_analyzer=context_analyzer,
            )

            conversational_agent = ConversationalAgent(
                service=self._agent_service,
                context_builder=context_builder,
                context_analyzer=context_analyzer,
                prompt_builder=prompt_builder,
                agent_chain=agent_chain,
            )

            self._registry.register(
                AgentCommand(
                    agent=conversational_agent,
                    task="",
                )
            )

            self._registry.register(
                OrchestratedAgentCommand(
                    service=self._agent_service,
                )
            )

