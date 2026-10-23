from pathlib import Path
from uuid import uuid4

from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.provider import AgentProvider


def test_engineering_context_contains_project_scope() -> None:
    root = Path("F:/EduNova")

    context = EngineeringContext(
        project_root=root,
        scope="academic-records",
    )

    assert context.project_root == root
    assert context.scope == "academic-records"


def test_engineering_context_has_safe_defaults() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
    )

    assert context.git_status == ()
    assert context.changed_files == ()
    assert context.tests == ()
    assert context.decisions == ()
    assert context.risks == ()


def test_engineering_context_is_immutable() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
    )

    try:
        context.scope = "other"
    except AttributeError:
        pass
    else:
        raise AssertionError("EngineeringContext must be immutable")


def test_provider_has_name() -> None:
    provider = AgentProvider(name="opencode")

    assert provider.name == "opencode"


def test_provider_rejects_empty_name() -> None:
    try:
        AgentProvider(name="")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty provider name must fail")
