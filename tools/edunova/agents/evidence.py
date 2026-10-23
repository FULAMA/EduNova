from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class EvidenceItem:
    path: str
    exists: bool
    content: str = ""
    start_line: int | None = None
    end_line: int | None = None


class TaskEvidenceCollector:
    _PATH_PATTERN = re.compile(
        r"(?:src|tools|tests|frontend)(?:[\\/][A-Za-z0-9_.-]+)+"
    )

    def __init__(self, project_root: Path, max_file_size: int = 20_000) -> None:
        self._project_root = project_root.resolve()
        self._max_file_size = max_file_size

    def collect(self, task: str) -> tuple[EvidenceItem, ...]:
        paths = self._extract_paths(task)
        evidence: list[EvidenceItem] = []

        for relative_path in paths:
            path = (self._project_root / relative_path).resolve()

            if not path.is_relative_to(self._project_root):
                evidence.append(
                    EvidenceItem(
                        path=relative_path,
                        exists=False,
                        content=(
                            "[CONTENT BLOCKED: path resolves outside the "
                            "project root]"
                        ),
                    )
                )
                continue

            if self._is_sensitive_path(path):
                evidence.append(
                    EvidenceItem(
                        path=relative_path,
                        exists=False,
                        content=(
                            "[CONTENT BLOCKED: sensitive file type is not "
                            "eligible for external agent evidence]"
                        ),
                    )
                )
                continue

            if not path.is_file():
                evidence.append(
                    EvidenceItem(
                        path=relative_path,
                        exists=False,
                    )
                )
                continue

            try:
                raw = path.read_bytes()

                if len(raw) > self._max_file_size:
                    evidence.append(
                        EvidenceItem(
                            path=relative_path,
                            exists=True,
                            content=(
                                f"[CONTENT OMITTED: file exceeds "
                                f"{self._max_file_size} bytes]"
                            ),
                        )
                    )
                    continue

                content = raw.decode("utf-8")

                line_count = len(content.splitlines())

                evidence.append(
                    EvidenceItem(
                        path=relative_path,
                        exists=True,
                        content=content,
                        start_line=1,
                        end_line=line_count,
                    )
                )
            except (OSError, UnicodeDecodeError) as exc:
                evidence.append(
                    EvidenceItem(
                        path=relative_path,
                        exists=True,
                        content=f"[CONTENT UNAVAILABLE: {type(exc).__name__}]",
                    )
                )

        return tuple(evidence)

    @staticmethod
    def _is_sensitive_path(path: Path) -> bool:
        name = path.name.casefold()
        suffix = path.suffix.casefold()

        return (
            name.startswith(".env")
            or name in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
            or suffix in {".pem", ".key", ".p12", ".pfx"}
        )

    def build_prompt_section(
        self,
        evidence: tuple[EvidenceItem, ...],
    ) -> str:
        lines = [
            "EXPLICIT FILE EVIDENCE:",
            "",
            "The following evidence was directly read from the project.",
            "Do not infer beyond the provided content.",
        ]

        if not evidence:
            lines.append("- No explicitly referenced project file was inspected.")
            return "\n".join(lines)

        for item in evidence:
            lines.extend(
                [
                    "",
                    f"FILE: {item.path}",
                    f"EXISTS: {'yes' if item.exists else 'no'}",
                    f"LINES: {item.start_line}-{item.end_line}" if item.start_line is not None else "LINES: unknown",
                ]
            )

            if item.exists:
                lines.extend(
                    [
                        "CONTENT:",
                        "```text",
                        item.content,
                        "```",
                    ]
                )

        return "\n".join(lines)

    def _extract_paths(self, task: str) -> tuple[str, ...]:
        found = self._PATH_PATTERN.findall(task)

        normalized: list[str] = []

        for path in found:
            clean = path.replace("\\", "/")

            if clean not in normalized:
                normalized.append(clean)

        return tuple(normalized)
