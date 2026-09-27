from tools.edunova.bootstrap import CliBootstrap
from tools.edunova.infrastructure.process_runner import ProcessRunner


def main(
    args: list[str],
    process_runner: ProcessRunner | None = None,
) -> int:
    bootstrap = CliBootstrap(process_runner=process_runner)
    result = bootstrap.dispatcher.dispatch(args[0])

    return result.exit_code
