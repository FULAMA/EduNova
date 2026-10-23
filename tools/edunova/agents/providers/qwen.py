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


class QwenClientFactory:
    def create(self, config: ProviderConfig) -> OpenAI:
        if config.name != "qwen":
            raise ValueError("QwenClientFactory requires provider 'qwen'.")

        api_key = os.getenv("DASHSCOPE_API_KEY")

        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY is required.")

        base_url = os.getenv(
            "QWEN_BASE_URL",
            "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )

        return OpenAI(
            api_key=api_key,
            base_url=base_url,
        )


class QwenProviderFactory:
    def __init__(self, client_factory: QwenClientFactory) -> None:
        self._client_factory = client_factory

    def create(self, config: ProviderConfig) -> "QwenAdapter":
        if config.name != "qwen":
            raise ValueError("QwenProviderFactory requires provider 'qwen'.")

        client = self._client_factory.create(config)

        return QwenAdapter(
            client=client,
            model=config.model,
            timeout=config.timeout,
        )


class QwenAdapter(ProviderAdapter):
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
                    message="Qwen returned an empty response.",
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
