from tools.edunova.agents.result import AgentResult, AgentRole


def test_agent_result_contains_execution_metadata() -> None:
    result = AgentResult(
        agent="groq",
        role=AgentRole.BUILDER,
        success=True,
        message="analysis",
        provider="groq",
        model="openai/gpt-oss-20b",
        duration_ms=125,
    )

    assert result.agent == "groq"
    assert result.role is AgentRole.BUILDER
    assert result.success is True
    assert result.provider == "groq"
    assert result.model == "openai/gpt-oss-20b"
    assert result.duration_ms == 125
    assert result.error is None
