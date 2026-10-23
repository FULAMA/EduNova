from pathlib import Path

from tools.edunova.agents.context_analyzer import (
    ContextAnalyzer,
    EngineeringAnalysis,
)
from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.prompt_builder import EngineeringPromptBuilder


def make_analysis(**overrides) -> EngineeringAnalysis:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="test-scope",
        git_branch="main",
        git_status=(" M src/example.py",),
        changed_files=("src/example.py",),
        architecture=("src/academic", "src/identity"),
        tests=("tests/unit", "tests/integration"),
        decisions=(),
        risks=(),
    )
    analysis = ContextAnalyzer().analyze(context)

    values = {
        "scope": analysis.scope,
        "git_branch": analysis.git_branch,
        "changed_files": analysis.changed_files,
        "architecture": analysis.architecture,
        "tests": analysis.tests,
        "decisions": analysis.decisions,
        "risks": analysis.risks,
        "is_clean": analysis.is_clean,
    }
    values.update(overrides)
    return EngineeringAnalysis(**values)


def test_build_contains_engineering_context_sections() -> None:
    prompt = EngineeringPromptBuilder().build(make_analysis())

    assert "EDUNOVA ENGINEERING CONTEXT" in prompt
    assert "Scope: test-scope" in prompt
    assert "Git branch: main" in prompt
    assert "Workspace clean: no" in prompt
    assert "src/example.py" in prompt
    assert "src/academic" in prompt
    assert "tests/unit" in prompt
    assert "Known decisions:" in prompt
    assert "Risks:" in prompt


def test_build_reports_empty_sections_explicitly() -> None:
    analysis = make_analysis(
        changed_files=(),
        architecture=(),
        tests=(),
        decisions=(),
        risks=(),
        is_clean=True,
    )

    prompt = EngineeringPromptBuilder().build(analysis)

    assert "Workspace clean: yes" in prompt
    assert "Changed files (0):" in prompt
    assert "- none" in prompt
    assert "- none detected" in prompt
    assert "- none recorded" in prompt


def test_build_does_not_invent_architecture_or_decisions() -> None:
    analysis = make_analysis(
        architecture=("src/academic",),
        decisions=(),
    )

    prompt = EngineeringPromptBuilder().build(analysis)

    assert "src/academic" in prompt
    assert "tenant_id" not in prompt
    assert "PostgreSQL" not in prompt
    assert "StudentAcademicRecord" not in prompt
