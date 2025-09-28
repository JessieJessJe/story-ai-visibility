"""Transcript ingestion utilities for the visibility agent."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from src.common.text import (
    keyword_hits,
    mask_terms,
    normalize_whitespace,
    strip_markup,
)
from src.common.types import StoryDocument, StoryMetadata

GLOBAL_MASK_TOKEN = "[MASK]"


@dataclass(frozen=True)
class MaskingSummary:
    """Outcome of applying provider masking to a story."""

    masked_text: str
    issues: Sequence[str]


def load_transcript(path: Path) -> str:
    """Load and lightly clean a transcript from disk."""

    raw = path.read_text(encoding="utf-8")
    return normalize_story_text(raw)


def normalize_story_text(value: str) -> str:
    """Strip lightweight markup and normalize whitespace."""

    return normalize_whitespace(strip_markup(value))


def audit_mask_integrity(value: str, terms: Iterable[str]) -> list[str]:
    """Return human-readable issues when provider terms remain in text."""

    hits = keyword_hits(value, terms)
    return [f"Unmasked term '{term}' found {count} time(s)." for term, count in hits.items()]


def mask_provider_terms(value: str, terms: Sequence[str], token: str = GLOBAL_MASK_TOKEN) -> MaskingSummary:
    """Apply masking to provider aliases and report any remaining occurrences."""

    masked = mask_terms(value, terms, token=token)
    issues = audit_mask_integrity(masked, terms)
    return MaskingSummary(masked_text=masked, issues=issues)


def _coalesce_aliases(metadata: StoryMetadata, provider_aliases: Sequence[str] | None) -> list[str]:
    aliases = list(provider_aliases or [])
    if metadata.provider_name:
        aliases.append(metadata.provider_name)
    if not aliases:
        raise ValueError("At least one provider alias is required for masking.")
    return aliases


def load_story_document(
    path: Path,
    metadata: StoryMetadata,
    provider_aliases: Sequence[str] | None = None,
    enforce_mask_integrity: bool = True,
) -> StoryDocument:
    """Ingest a story file, normalize content, and apply provider masking."""

    raw = path.read_text(encoding="utf-8")
    return load_story_document_from_text(
        raw,
        metadata,
        provider_aliases=provider_aliases,
        enforce_mask_integrity=enforce_mask_integrity,
    )


def load_story_document_from_text(
    text: str,
    metadata: StoryMetadata,
    provider_aliases: Sequence[str] | None = None,
    enforce_mask_integrity: bool = True,
) -> StoryDocument:
    """Normalize and mask a story directly from a string."""

    normalized = normalize_story_text(text)
    aliases = _coalesce_aliases(metadata, provider_aliases)
    summary = mask_provider_terms(normalized, aliases)
    if enforce_mask_integrity and summary.issues:
        raise ValueError("; ".join(summary.issues))

    return StoryDocument(
        metadata=metadata,
        raw_text=text,
        normalized_text=normalized,
        masked_text=summary.masked_text,
    )


__all__ = [
    "GLOBAL_MASK_TOKEN",
    "MaskingSummary",
    "load_transcript",
    "normalize_story_text",
    "audit_mask_integrity",
    "mask_provider_terms",
    "load_story_document",
    "load_story_document_from_text",
]
