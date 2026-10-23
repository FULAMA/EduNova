import os
from time import perf_counter

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole
from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.adapter import ProviderAdapter


class MistralClientFactory:
    def create(self, config: ProviderConfig) -> OpenAI:
        if config.name != "mistral":
            raise ValueError("MistralClientFactory requires provider 'mistral'.")

        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            raise ValueError("MISTRAL_API_KEY is required.")

        return OpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1",
        )


class MistralProviderFactory:
    def __init__(self, client_factory: MistralClientFactory) -> None:
        self._client_factory = client_factory

    def create(self, config: ProviderConfig) -> "MistralAdapter":
        if config.name != "mistral":
            raise ValueError("MistralProviderFactory requires provider 'mistral'.")

        client = self._client_factory.create(config)

        return MistralAdapter(
            client=client,
            model=config.model,
            timeout=config.timeout,
        )


class MistralAdapter(ProviderAdapter):
    def __init__(
        self,
        client: OpenAI,
        model: str,
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
        started = perf_counter()

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

            content = response.choices[0].message.content

            if not content:
                return AgentResult(
                    agent=provider.name,
                    role=AgentRole.BUILDER,
                    success=False,
                    message="Mistral returned an empty response.",
                    provider=provider.name,
                    model=self._model,
                    duration_ms=int((perf_counter() - started) * 1000),
                    error="empty_response",
                )

            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=True,
                message=content,
                provider=provider.name,
                model=self._model,
                duration_ms=int((perf_counter() - started) * 1000),
            )

        except AuthenticationError as exc:
            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message=str(exc),
                provider=provider.name,
                model=self._model,
                duration_ms=int((perf_counter() - started) * 1000),
                error="authentication_error",
            )

        except RateLimitError as exc:
            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message=str(exc),
                provider=provider.name,
                model=self._model,
                duration_ms=int((perf_counter() - started) * 1000),
                error="rate_limit",
            )

        except APITimeoutError as exc:
            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message=str(exc),
                provider=provider.name,
                model=self._model,
                duration_ms=int((perf_counter() - started) * 1000),
                error="timeout",
            )

        except APIConnectionError as exc:
            return AgentResult(
                agent=provider.name,
                role=AgentRole.BUILDER,
                success=False,
                message=str(exc),
                provider=provider.name,
                model=self._model,
                duration_ms=int((perf_counter() - started) * 1000),
                error="connection_error",
            )
