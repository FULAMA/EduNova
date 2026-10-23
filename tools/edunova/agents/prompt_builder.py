from tools.edunova.agents.context_analyzer import EngineeringAnalysis


class EngineeringPromptBuilder:
    def build(self, analysis: EngineeringAnalysis) -> str:
        lines = [
            "EDUNOVA ENGINEERING CONTEXT",
            "",
            "IMPORTANT: The following information is observed project evidence.",
            "Do not infer implementation details that are not explicitly present.",
            "",
            f"Scope: {analysis.scope}",
            f"Git branch: {analysis.git_branch or 'unknown'}",
            f"Workspace clean: {'yes' if analysis.is_clean else 'no'}",
            "",
            f"Git changes ({len(analysis.git_changes)}):",
        ]

        if analysis.git_changes:
            for change in analysis.git_changes:
                lines.append(
                    f"- status={change.status!r} path={change.path}"
                )
        else:
            lines.append("- none")

        lines.extend(
            [
                "",
                f"Changed files ({analysis.changed_file_count}):",
            ]
        )

        if analysis.changed_files:
            lines.extend(
                f"- {path}"
                for path in analysis.changed_files
            )
        else:
            lines.append("- none")

        lines.extend(
            [
                "",
                "Known architecture:",
            ]
        )

        if analysis.architecture:
            lines.extend(
                f"- {item}"
                for item in analysis.architecture
            )
        else:
            lines.append("- none detected")

        lines.extend(
            [
                "",
                "Known test areas:",
            ]
        )

        if analysis.tests:
            lines.extend(
                f"- {item}"
                for item in analysis.tests
            )
        else:
            lines.append("- none detected")

        lines.extend(
            [
                "",
                "Known decisions:",
            ]
        )

        if analysis.decisions:
            lines.extend(
                f"- {item}"
                for item in analysis.decisions
            )
        else:
            lines.append("- none recorded")

        lines.extend(
            [
                "",
                "Risks:",
            ]
        )

        if analysis.risks:
            lines.extend(
                f"- {item}"
                for item in analysis.risks
            )
        else:
            lines.append("- none detected")

        return "\n".join(lines)
