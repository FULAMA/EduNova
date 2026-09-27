from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.infrastructure.process_runner import ProcessRunner


class RunTestsCommand(Command):
    name = "run_tests"

    def __init__(self, process_runner: ProcessRunner) -> None:
        self._process_runner = process_runner

    def execute(self) -> CommandResult:
        result = self._process_runner.run(["pytest"])

        status = (
            Status.SAFE
            if result.returncode == 0
            else Status.FAIL
        )

        message = result.stdout.strip() or result.stderr.strip()

        return CommandResult(
            command=self.name,
            status=status,
            message=message,
            exit_code=result.returncode,
        )
