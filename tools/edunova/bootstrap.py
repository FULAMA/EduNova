from tools.edunova.commands.run_tests import RunTestsCommand
from tools.edunova.commands.work import WorkCommand
from tools.edunova.core.dispatcher import CommandDispatcher
from tools.edunova.core.command_registry import CommandRegistry
from tools.edunova.core.command_service import CommandService
from tools.edunova.core.runner import CommandRunner
from tools.edunova.infrastructure.process_runner import ProcessRunner


class CliBootstrap:
    def __init__(
        self,
        process_runner: ProcessRunner | None = None,
    ) -> None:
        self._registry = CommandRegistry()
        self._runner = CommandRunner()
        self._process_runner = process_runner or ProcessRunner()

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
        run_tests = RunTestsCommand(self._process_runner)

        self._registry.register(run_tests)
        self._registry.register(
            WorkCommand([run_tests])
        )
