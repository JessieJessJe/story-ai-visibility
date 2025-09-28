"""Shared domain types for visibility processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class StoryMetadata:
    """Source information for a visibility story."""

    story_id: str
    source_url: str | None = None
    client_name: str | None = None
    provider_name: str = ""


@dataclass
class StoryDocument:
    """Normalized and masked story content ready for downstream processing."""

    metadata: StoryMetadata
    raw_text: str
    normalized_text: str
    masked_text: str


@dataclass
class NarrativePillar:
    """Represents a prioritized visibility signal."""

    title: str
    summary: str
    evidence: List[str] = field(default_factory=list)
    priority: int | None = None


@dataclass
class ClarifyingQuestion:
    """Question analysts should ask to improve visibility confidence."""

    prompt: str
    category: str = "discovery"
    kind: str = "industry_general"
    identifier: str | None = None
    assumptions: List[str] = field(default_factory=list)


@dataclass
class VisibilityScorecard:
    """Collection of scalar scores that describe the output."""

    coverage: float = 0.0
    confidence: float = 0.0


@dataclass
class QuestionAnswer:
    """Model answer paired with metadata for evaluation."""

    question_id: str
    model: str
    prompt: str
    answer: str
    kind: str
    ai_provider_inferred: bool = False


@dataclass
class VisibilitySummary:
    """High-level visibility metrics for quick reporting."""

    total_questions: int = 0
    ai_provider_recognized_in: int = 0


@dataclass
class VisibilityResult:
    """Full artifact persisted by the pipeline."""

    story_id: str
    pillars: List[NarrativePillar]
    questions: List[ClarifyingQuestion]
    answers: List[QuestionAnswer]
    scores: VisibilityScorecard
    summary: VisibilitySummary
    generated_at: datetime = field(default_factory=datetime.utcnow)
    models_run: List[str] = field(default_factory=list)
    metadata: StoryMetadata | None = None
    mode: str | None = None


__all__ = [
    "StoryMetadata",
    "StoryDocument",
    "NarrativePillar",
    "ClarifyingQuestion",
    "VisibilityScorecard",
    "QuestionAnswer",
    "VisibilitySummary",
    "VisibilityResult",
]
