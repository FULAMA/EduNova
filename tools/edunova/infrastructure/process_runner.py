import subprocess
from collections.abc import Sequence
from pathlib import Path


class ProcessRunner:
    def __init__(self, timeout: float | None = 600) -> None:
        if timeout is not None and timeout <= 0:
            raise ValueError("Process timeout must be greater than zero.")

        self._timeout = timeout

    def run(
        self,
        command: Sequence[str],
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
            timeout=self._timeout,
        )
