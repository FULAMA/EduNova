from collections.abc import Sequence
import os
from pathlib import Path
import shutil
import sys


def tool_command(name: str, arguments: Sequence[str]) -> list[str]:
    """Resolve a fixed tool beside Python first, then through PATH."""
    executable_name = f"{name}.exe" if os.name == "nt" else name
    sibling = Path(sys.executable).resolve().parent / executable_name
    executable = str(sibling) if sibling.is_file() else shutil.which(name)
    return [executable or name, *arguments]
