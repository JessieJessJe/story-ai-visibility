"""Configuration helpers for the visibility agents."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class ModelSettings:
    """Settings that control which model provider and variant to use."""

    provider: str = "openai"
    name: str = "gpt-4o"
    temperature: float = 0.2


@dataclass
class StorageSettings:
    """Settings for persistence layers used by the pipeline."""

    bucket: str = "local-cache"
    base_path: str = "visibility-results"


@dataclass
class Settings:
    """Aggregated application configuration."""

    model: ModelSettings
    storage: StorageSettings


def load_settings() -> Settings:
    """Load settings from environment variables with safe defaults."""

    model = ModelSettings(
        provider=os.getenv("MODEL_PROVIDER", "openai"),
        name=os.getenv("MODEL_NAME", "gpt-4o"),
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0.2")),
    )
    storage = StorageSettings(
        bucket=os.getenv("STORAGE_BUCKET", "local-cache"),
        base_path=os.getenv("STORAGE_BASE_PATH", "visibility-results"),
    )
    return Settings(model=model, storage=storage)


__all__ = ["ModelSettings", "StorageSettings", "Settings", "load_settings"]
