from tools.edunova.__main__ import main as module_main
from tools.edunova.cli import main
from tools.edunova.infrastructure.process_runner import ProcessRunner


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


def test_cli_main_returns_zero_for_run_tests() -> None:
    process_runner = FakeProcessRunner()

    exit_code = main(
        ["run_tests"],
        process_runner=process_runner,
    )

    assert exit_code == 0


def test_module_entrypoint_forwards_arguments_to_cli() -> None:
    process_runner = FakeProcessRunner()

    exit_code = module_main(
        ["run_tests"],
        process_runner=process_runner,
    )

    assert exit_code == 0
    assert process_runner.commands == [["pytest"]]
