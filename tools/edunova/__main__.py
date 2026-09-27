import sys

from tools.edunova.cli import main as cli_main
from tools.edunova.infrastructure.process_runner import ProcessRunner


def main(
    args: list[str] | None = None,
    process_runner: ProcessRunner | None = None,
) -> int:
    command_args = sys.argv[1:] if args is None else args

    return cli_main(command_args, process_runner=process_runner)


if __name__ == "__main__":
    raise SystemExit(main())
