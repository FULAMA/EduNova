import subprocess
from collections.abc import Sequence


class ProcessRunner:
    def run(
        self,
        command: Sequence[str],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
