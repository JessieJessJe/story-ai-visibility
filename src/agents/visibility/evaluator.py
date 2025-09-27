"""Evaluate visibility outputs to generate lightweight scorecards."""

from __future__ import annotations

from typing import Iterable

from src.common.text import keyword_hits
from src.common.types import QuestionAnswer, VisibilityResult, VisibilityScorecard, VisibilitySummary


def detect_provider_in_answer(answer: QuestionAnswer, provider_aliases: Iterable[str]) -> bool:
    """Return True when the answer cites any provider alias."""

    hits = keyword_hits(answer.answer, provider_aliases)
    return bool(hits)


def evaluate_answers(result: VisibilityResult, provider_aliases: Iterable[str]) -> None:
    """Mutate answers with provider inference flags and refresh summary."""

    question_hits: dict[str, bool] = {}
    for answer in result.answers:
        seen = detect_provider_in_answer(answer, provider_aliases)
        answer.ai_provider_inferred = seen
        if answer.question_id not in question_hits:
            question_hits[answer.question_id] = seen
        else:
            question_hits[answer.question_id] = question_hits[answer.question_id] or seen

    total_questions = len(question_hits) if question_hits else len(result.questions)
    inferred = sum(1 for hit in question_hits.values() if hit)
    result.summary = VisibilitySummary(total_questions=total_questions, ai_provider_recognized_in=inferred)


def score_visibility(result: VisibilityResult, provider_aliases: Iterable[str]) -> VisibilityScorecard:
    """Compute coverage and confidence scores after evaluation."""

    evaluate_answers(result, provider_aliases)
    total_questions = max(1, result.summary.total_questions)
    coverage = result.summary.ai_provider_recognized_in / total_questions
    confidence = min(1.0, 0.1 * (len(result.pillars) + result.summary.ai_provider_recognized_in))
    scorecard = VisibilityScorecard(coverage=coverage, confidence=confidence)
    result.scores = scorecard
    return scorecard


__all__ = ["detect_provider_in_answer", "evaluate_answers", "score_visibility"]
