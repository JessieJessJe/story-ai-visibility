"""Extract visibility pillars from transcripts."""

from __future__ import annotations

import itertools
import re
from typing import Iterable, List, Sequence

from src.common.text import split_paragraphs
from src.common.types import NarrativePillar

_KEYWORD_TITLE_MAP: Sequence[tuple[tuple[str, ...], str]] = (
    (("adoption", "expansion", "pilot"), "Adoption Momentum"),
    (("engagement", "usage", "retention"), "Content Engagement"),
    (("revenue", "monetization", "pricing"), "Monetization Blockers"),
    (("feedback", "trust", "quality"), "Trust Through Feedback"),
    (("evaluation", "benchmark", "metrics"), "Rigorous Evaluations"),
    (("latency", "speed", "efficiency"), "Operational Efficiency"),
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?]) +")


def _infer_title(paragraph: str, fallback_index: int) -> str:
    lowered = paragraph.lower()
    for keywords, title in _KEYWORD_TITLE_MAP:
        if any(keyword in lowered for keyword in keywords):
            return title

    words = [word for word in paragraph.split() if word]
    if not words:
        return f"Signal {fallback_index}"
    snippet = " ".join(words[:3]).title()
    return snippet or f"Signal {fallback_index}"


def _summarize(paragraph: str) -> str:
    sentences = _SENTENCE_SPLIT_RE.split(paragraph.strip())
    if sentences:
        return sentences[0][:200]
    return paragraph[:200]


def extract_pillars(transcript: str, target_count: int = 3) -> List[NarrativePillar]:
    """Derive prioritized visibility pillars from transcript content."""

    if not transcript.strip():
        return []

    paragraphs = split_paragraphs(transcript)
    if not paragraphs:
        paragraphs = [transcript.strip()]
    if len(paragraphs) < target_count:
        sentences = [segment.strip() for segment in _SENTENCE_SPLIT_RE.split(transcript) if segment.strip()]
        if sentences:
            paragraphs = sentences

    scored = sorted(paragraphs, key=len, reverse=True)
    selected = list(itertools.islice(scored, target_count)) or paragraphs[:target_count]

    pillars: List[NarrativePillar] = []
    seen_titles: set[str] = set()
    for index, paragraph in enumerate(selected, start=1):
        title = _infer_title(paragraph, index)
        key = title.lower()
        if key in seen_titles:
            title = f"{title} {index}"
            key = title.lower()
        seen_titles.add(key)
        pillars.append(
            NarrativePillar(
                title=title,
                summary=_summarize(paragraph),
                evidence=[paragraph.strip()],
                priority=index,
            )
        )
    return pillars


def merge_pillars(pillars: Iterable[NarrativePillar]) -> List[NarrativePillar]:
    """Return pillars sorted by priority, removing duplicates by title."""

    unique: dict[str, NarrativePillar] = {}
    for pillar in pillars:
        title_key = pillar.title.lower()
        if title_key not in unique:
            unique[title_key] = pillar
        else:
            existing = unique[title_key]
            if pillar.priority is not None and (existing.priority is None or pillar.priority < existing.priority):
                unique[title_key] = pillar
    ordered = sorted(unique.values(), key=lambda item: item.priority or 99)
    return ordered


__all__ = ["extract_pillars", "merge_pillars"]
