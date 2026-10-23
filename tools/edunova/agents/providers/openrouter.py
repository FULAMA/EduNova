import os
from time import perf_counter

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from tools.edunova.agents.orchestration.adapter import ProviderAdapter
from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class OpenRouterClientFactory:
    def create(self, config: ProviderConfig):
        if config.name != "openrouter":
            raise ValueError(
                "OpenRouterClientFactory requires provider 'openrouter'."
            )

        api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required.")

        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )


class OpenRouterProviderFactory:
    def __init__(
        self,
        client_factory: OpenRouterClientFactory,
    ) -> None:
        self._client_factory = client_factory

    def create(self, config: ProviderConfig) -> "OpenRouterAdapter":
        if config.name != "openrouter":
            raise ValueError(
                "OpenRouterProviderFactory requires provider 'openrouter'."
            )

        client = self._client_factory.create(config)

        model = config.model.strip() or "openrouter/free"

        return OpenRouterAdapter(
            client=client,
            model=model,
            timeout=config.timeout,
        )


class OpenRouterAdapter(ProviderAdapter):
    name = "openrouter"

    def __init__(
        self,
        client,
        model: str = "openrouter/free",
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
                    message="OpenRouter returned an empty response.",
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
                message="OpenRouter authentication failed.",
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
                message="OpenRouter rate limit reached.",
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
                message="OpenRouter request timed out.",
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
                message="OpenRouter connection failed.",
                provider=provider.name,
                model=self._model,
                duration_ms=duration_ms,
                error="connection_error",
            )
