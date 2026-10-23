from time import perf_counter

from groq import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)

from tools.edunova.agents.orchestration.adapter import ProviderAdapter
from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class GroqClientFactory:
    def create(self, config: ProviderConfig):
        if config.name != "groq":
            raise ValueError("GroqClientFactory requires provider 'groq'.")

        import os

        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is required.")

        return Groq(api_key=api_key)


class GroqProviderFactory:
    def __init__(self, client_factory: GroqClientFactory) -> None:
        self._client_factory = client_factory

    def create(self, config: ProviderConfig) -> "GroqAdapter":
        if config.name != "groq":
            raise ValueError("GroqProviderFactory requires provider 'groq'.")

        client = self._client_factory.create(config)

        model = config.model.strip() or "openai/gpt-oss-20b"

        return GroqAdapter(
            client=client,
            model=model,
            timeout=config.timeout,
        )


class GroqAdapter(ProviderAdapter):
    name = "groq"

    def __init__(
        self,
        client,
        model: str = "openai/gpt-oss-20b",
        timeout: int = 60,
    ) -> None:
        self._client = client
        self._model = model
        self._timeout = timeout

    def generate(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        if not task.strip():
            raise ValueError("Task cannot be empty.")

        started_at = perf_counter()

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": task,
                    }
                ],
                timeout=self._timeout,
            )

            duration_ms = int((perf_counter() - started_at) * 1000)
            content = response.choices[0].message.content

            if not content:
                return AgentResult(
                    agent=provider.name,
                    role=AgentRole.BUILDER,
                    success=False,
                    message="Groq returned an empty response.",
                    provider=provider.name,
                    model=self._model,
                    duration_ms=duration_ms,
                    error="empty_response",
                )

            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=True,
                message=content,
                provider=provider.name,
                model=self._model,
                duration_ms=duration_ms,
            )

        except AuthenticationError:
            duration_ms = int((perf_counter() - started_at) * 1000)

            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message="Groq authentication failed.",
                provider=provider.name,
                model=self._model,
                duration_ms=duration_ms,
                error="authentication_error",
            )

        except RateLimitError:
            duration_ms = int((perf_counter() - started_at) * 1000)

            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message="Groq rate limit reached.",
                provider=provider.name,
                model=self._model,
                duration_ms=duration_ms,
                error="rate_limit",
            )

        except APITimeoutError:
            duration_ms = int((perf_counter() - started_at) * 1000)

            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message="Groq request timed out.",
                provider=provider.name,
                model=self._model,
                duration_ms=duration_ms,
                error="timeout",
            )

        except APIConnectionError:
            duration_ms = int((perf_counter() - started_at) * 1000)

            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message="Groq connection failed.",
                provider=provider.name,
                model=self._model,
                duration_ms=duration_ms,
                error="connection_error",
            )
