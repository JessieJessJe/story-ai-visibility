"""High-level pipeline orchestration reusable by CLI and FastAPI."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Iterable, Sequence

from src.agents.visibility.evaluator import score_visibility
from src.agents.visibility.ingestion import load_story_document_from_text
from src.agents.visibility.model_runner import ModelRunner
from src.agents.visibility.service import VisibilityLLMService
from src.agents.visibility.storage import serialize_result
from src.common.config import Settings, load_settings
from src.common.types import (
    ClarifyingQuestion,
    StoryMetadata,
    VisibilityResult,
    VisibilityScorecard,
    VisibilitySummary,
)


def _generate_story_id(text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"story-{digest}"


def _dedupe(sequence: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in sequence:
        if not item:
            continue
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _prepare_settings(settings: Settings, mode: str | None) -> Settings:
    final_mode = mode or settings.model.mode
    if final_mode == settings.model.mode:
        return settings
    model = replace(settings.model, mode=final_mode)
    return replace(settings, model=model)


def run_pipeline(
    *,
    text: str,
    provider_name: str | None = None,
    provider_aliases: Sequence[str] | None = None,
    mode: str | None = None,
    story_id: str | None = None,
    client_name: str | None = None,
    source_url: str | None = None,
    settings: Settings | None = None,
    models_override: Sequence[str] | None = None,
) -> dict:
    """Execute the visibility pipeline and return the serialized result."""

    settings = settings or load_settings()
    effective_mode = mode or settings.model.mode
    settings = _prepare_settings(settings, effective_mode)

    provider_name = provider_name or settings.provider.name
    aliases = list(provider_aliases or settings.provider.aliases)
    aliases = _dedupe(aliases)

    metadata = StoryMetadata(
        story_id=story_id or _generate_story_id(text),
        source_url=source_url,
        client_name=client_name,
        provider_name=provider_name,
    )

    document = load_story_document_from_text(
        text,
        metadata,
        provider_aliases=aliases,
    )

    service = VisibilityLLMService(settings, ModelRunner(settings))

    pillars = service.extract_pillars(document)
    questions = service.generate_questions(pillars)

    if models_override:
        models = _dedupe(models_override)
    else:
        models = _dedupe([settings.model.name, *settings.model.comparison_models])
    answers = service.build_answers(models, questions, transcript=document.masked_text)

    result = VisibilityResult(
        story_id=metadata.story_id,
        pillars=pillars,
        questions=questions,
        answers=answers,
        scores=VisibilityScorecard(),
        summary=VisibilitySummary(),
        models_run=models,
        metadata=metadata,
        mode=effective_mode,
    )

    provider_terms = _dedupe([metadata.provider_name, *aliases])
    score_visibility(result, provider_terms)

    payload = serialize_result(result)
    metadata_payload = payload.setdefault("metadata", {})
    metadata_payload.setdefault("provider_name", provider_name)
    metadata_payload.setdefault("client_name", client_name)
    metadata_payload.setdefault("source_url", source_url)
    metadata_payload["mode"] = effective_mode
    return payload


__all__ = ["run_pipeline"]
