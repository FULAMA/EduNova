from tools.edunova.bootstrap import CliBootstrap
from tools.edunova.infrastructure.process_runner import ProcessRunner


def test_bootstrap_creates_registry() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry is not None


def test_bootstrap_registers_run_tests_command() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry.has("run_tests")


def test_bootstrap_registers_work_command() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry.has("work")


def test_bootstrap_creates_command_service() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.service is not None


def test_bootstrap_uses_command_runner() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.runner is not None

def test_bootstrap_creates_command_dispatcher() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.dispatcher is not None

def test_bootstrap_dispatcher_can_execute_run_tests() -> None:
    bootstrap = CliBootstrap()

    result = bootstrap.dispatcher.dispatch("run_tests")

    assert result.command == "run_tests"


def test_bootstrap_accepts_process_runner() -> None:
    process_runner = ProcessRunner()

    bootstrap = CliBootstrap(process_runner=process_runner)

    assert bootstrap is not None

class FakeProcessRunner(ProcessRunner):
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(self, command: list[str]):
        self.commands.append(command)

        class FakeResult:
            returncode = 0
            stdout = "fake tests passed"
            stderr = ""

        return FakeResult()


def test_bootstrap_uses_injected_process_runner() -> None:
    process_runner = FakeProcessRunner()
    bootstrap = CliBootstrap(process_runner=process_runner)

    result = bootstrap.dispatcher.dispatch("run_tests")

    assert process_runner.commands == [["pytest"]]
    assert result.status.value == "SAFE"

