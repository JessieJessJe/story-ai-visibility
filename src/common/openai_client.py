"""Thin wrapper around the OpenAI client with retry and backoff."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from src.common.config import ModelSettings

try:  # pragma: no cover - live dependency
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled in code
    OpenAI = None  # type: ignore


@dataclass
class OpenAIClientConfig:
    api_key: str
    organization: str | None
    timeout_seconds: float
    max_retries: int
    backoff_seconds: float


class OpenAIClient:
    """Wrapper that provides chat completion with retry & rate limit handling."""

    def __init__(self, config: OpenAIClientConfig) -> None:
        if not config.api_key:
            raise ValueError("OPENAI_API_KEY is required for live mode.")
        if OpenAI is None:
            raise ImportError(
                "The 'openai' package is required for live mode. Install it via 'pip install openai'."
            )
        self._config = config
        self._client = OpenAI(api_key=config.api_key, organization=config.organization)

    @classmethod
    def from_model_settings(cls, settings: ModelSettings) -> OpenAIClient:
        if settings.api_key is None:
            raise ValueError("OPENAI_API_KEY must be set when MODEL_MODE=live.")
        config = OpenAIClientConfig(
            api_key=settings.api_key,
            organization=settings.organization,
            timeout_seconds=settings.timeout_seconds,
            max_retries=settings.max_retries,
            backoff_seconds=settings.backoff_seconds,
        )
        return cls(config)

    def chat(  # pragma: no cover - requires live API
        self,
        *,
        model: str,
        messages: Iterable[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]] = None,
        reasoning_effort: Optional[str] = None,
        max_reasoning_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Call the chat completions endpoint with retry/backoff."""

        for attempt in range(self._config.max_retries + 1):
            try:
                messages_list = list(messages)
                if model.startswith("gpt-5"):
                    inputs: List[Dict[str, Any]] = [
                        {
                            "role": message.get("role", "user"),
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": message.get("content", ""),
                                }
                            ],
                        }
                        for message in messages_list
                    ]
                    response = self._client.responses.create(  # type: ignore[attr-defined]
                        model=model,
                        input=inputs,
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        timeout=self._config.timeout_seconds,
                    )
                    if hasattr(response, "model_dump"):
                        result = response.model_dump()
                        result["output_text"] = getattr(response, "output_text", "")
                        return result
                    return {
                        "output_text": getattr(response, "output_text", ""),
                        "response": response,
                    }

                kwargs: Dict[str, Any] = {
                    "model": model,
                    "messages": messages_list,
                    "temperature": temperature,
                    "max_completion_tokens": max_tokens,
                    "timeout": self._config.timeout_seconds,
                    "response_format": response_format,
                }
                if max_reasoning_tokens is not None and model.startswith("gpt-5"):
                    kwargs["max_reasoning_tokens"] = max_reasoning_tokens
                result = self._client.chat.completions.create(  # type: ignore[attr-defined]
                    **kwargs,
                )
                if hasattr(result, "model_dump"):
                    return result.model_dump()  # OpenAI >= 1.0
                if hasattr(result, "to_dict"):
                    return result.to_dict()  # Legacy clients
                return dict(result) if isinstance(result, dict) else {"response": result}
            except Exception as exc:
                if attempt >= self._config.max_retries:
                    raise
                sleep_seconds = self._config.backoff_seconds * (2 ** attempt)
                time.sleep(sleep_seconds)
        raise RuntimeError("OpenAI chat completion failed after retries.")


__all__ = ["OpenAIClient", "OpenAIClientConfig"]
