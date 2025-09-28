"""Configuration helpers for the visibility agents."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class ModelSettings:
    """Settings that control which model provider and variant to use."""

    provider: str = "openai"
    name: str = "gpt-5"
    temperature: float = 1.0
    mode: str = "stub"
    comparison_models: list[str] = field(default_factory=lambda: ["gpt-4o"])
    max_output_tokens: int = 4096
    max_retries: int = 2
    backoff_seconds: float = 2.0
    call_budget: int | None = 16
    timeout_seconds: float = 45.0
    api_key: str | None = None
    organization: str | None = None
    reasoning_effort: str | None = None
    max_reasoning_tokens: int | None = None


@dataclass
class StorageSettings:
    """Settings for persistence layers used by the pipeline."""

    bucket: str = "local-cache"
    base_path: str = "visibility-results"


@dataclass
class ProviderSettings:
    """Default provider metadata used throughout the pipeline."""

    name: str = "OpenAI"
    aliases: list[str] = field(
        default_factory=lambda: [
            "OpenAI",
            "Open AI",
            "OpenAI, Inc.",
            "ChatGPT",
            "GPT-4o",
            "GPT-5",
            "Sora",
            "DALL·E",
        ]
    )


@dataclass
class Settings:
    """Aggregated application configuration."""

    model: ModelSettings
    storage: StorageSettings
    provider: ProviderSettings




def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if not value or value.lower() == 'none':
        return None
    return int(value)


def _sanitize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _load_aliases(raw: str | None) -> list[str]:
    if not raw:
        return ProviderSettings().aliases
    raw = raw.strip()
    if not raw:
        return ProviderSettings().aliases
    try:
        loaded = json.loads(raw)
        if isinstance(loaded, list):
            return [str(item).strip() for item in loaded if str(item).strip()]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in raw.split(",") if item.strip()]

def load_settings() -> Settings:
    """Load settings from environment variables with safe defaults."""

    model = ModelSettings(
        provider=os.getenv("MODEL_PROVIDER", "openai"),
        name=os.getenv("MODEL_NAME", "gpt-5"),
        temperature=float(os.getenv("MODEL_TEMPERATURE", "1.0")),
        mode=os.getenv("MODEL_MODE", "stub"),
        comparison_models=[
            value.strip()
            for value in os.getenv("MODEL_COMPARISON_MODELS", "gpt-4o").split(",")
            if value.strip()
        ],
        max_output_tokens=int(os.getenv("MODEL_MAX_OUTPUT_TOKENS", "4096")),
        max_retries=int(os.getenv("MODEL_MAX_RETRIES", "2")),
        backoff_seconds=float(os.getenv("MODEL_BACKOFF_SECONDS", "2.0")),
        call_budget=_safe_int(os.getenv("MODEL_CALL_BUDGET", "20")),
        timeout_seconds=float(os.getenv("MODEL_TIMEOUT_SECONDS", "60")),
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORG", None),
        reasoning_effort=_sanitize_optional(os.getenv("MODEL_REASONING_EFFORT")),
        max_reasoning_tokens=_safe_int(os.getenv("MODEL_MAX_REASONING_TOKENS")),
    )
    storage = StorageSettings(
        bucket=os.getenv("STORAGE_BUCKET", "local-cache"),
        base_path=os.getenv("STORAGE_BASE_PATH", "visibility-results"),
    )
    provider = ProviderSettings(
        name=os.getenv("OPENAI_PROVIDER_NAME", "OpenAI"),
        aliases=_load_aliases(os.getenv("OPENAI_PROVIDER_ALIASES")),
    )
    return Settings(model=model, storage=storage, provider=provider)


__all__ = [
    "ModelSettings",
    "StorageSettings",
    "ProviderSettings",
    "Settings",
    "load_settings",
]
