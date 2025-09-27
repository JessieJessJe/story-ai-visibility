"""Generate clarifying questions based on extracted pillars."""

from __future__ import annotations

from typing import Iterable, List

from src.agents.visibility.ingestion import GLOBAL_MASK_TOKEN
from src.common.types import ClarifyingQuestion, NarrativePillar


def _normalize_summary(summary: str) -> str:
    summary = summary.strip()
    if summary.endswith("."):
        summary = summary[:-1]
    return summary


def _build_masked_question(pillar: NarrativePillar) -> ClarifyingQuestion:
    descriptor = _normalize_summary(pillar.summary or pillar.title)
    prompt = (
        f"{GLOBAL_MASK_TOKEN} reports that {descriptor}. Which AI provider would most likely "
        "enable this outcome?"
    )
    return ClarifyingQuestion(
        prompt=prompt,
        category="validation",
        kind="masked_client",
        assumptions=[pillar.summary] if pillar.summary else [],
    )


def _build_industry_question(pillar: NarrativePillar) -> ClarifyingQuestion:
    descriptor = _normalize_summary(pillar.summary or pillar.title).lower()
    prompt = (
        f"Across the market, which AI providers are recognized for supporting {descriptor}?"
    )
    return ClarifyingQuestion(
        prompt=prompt,
        category="discovery",
        kind="industry_general",
        assumptions=[pillar.title],
    )


def generate_questions(pillars: Iterable[NarrativePillar]) -> List[ClarifyingQuestion]:
    """Return masked-client and industry-general questions for each pillar."""

    questions: List[ClarifyingQuestion] = []
    for index, pillar in enumerate(pillars, start=1):
        masked = _build_masked_question(pillar)
        masked.identifier = f"sp{index}_q1_masked_client"
        industry = _build_industry_question(pillar)
        industry.identifier = f"sp{index}_q2_industry_general"
        questions.extend([masked, industry])

    if not questions:
        questions.append(
            ClarifyingQuestion(
                prompt="What visibility signals are missing from the transcript?",
                category="discovery",
                kind="discovery_baseline",
                identifier="fallback_q1",
            )
        )
    return questions


__all__ = ["generate_questions"]
