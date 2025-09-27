"""Storage helpers for visibility artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from src.common.types import ClarifyingQuestion, VisibilityResult


def _serialize_questions(
    pillar_index: int,
    questions: List[ClarifyingQuestion],
    result: VisibilityResult,
) -> List[Dict[str, object]]:
    question_map = {question.identifier: question for question in questions if question.identifier}
    answer_map = {answer.question_id: answer for answer in result.answers}

    serialized: List[Dict[str, object]] = []
    for suffix in ("q1_masked_client", "q2_industry_general"):
        question_id = f"sp{pillar_index}_{suffix}"
        question = question_map.get(question_id)
        answer = answer_map.get(question_id)
        if question is None or answer is None:
            continue
        serialized.append(
            {
                "id": question_id,
                "prompt": question.prompt,
                "answer": answer.answer,
                "ai_provider_inferred": answer.ai_provider_inferred,
                "model": answer.model,
            }
        )
    return serialized


def serialize_result(result: VisibilityResult) -> dict:
    """Convert a VisibilityResult into a JSON-serializable dictionary."""

    selling_points: List[Dict[str, object]] = []
    for index, pillar in enumerate(result.pillars, start=1):
        selling_points.append(
            {
                "pillar": pillar.title,
                "summary": pillar.summary,
                "questions": _serialize_questions(index, result.questions, result),
            }
        )

    payload: Dict[str, object] = {
        "story_id": result.story_id,
        "selling_points": selling_points,
        "scores": {
            "coverage": result.scores.coverage,
            "confidence": result.scores.confidence,
        },
        "summary": {
            "total_questions": result.summary.total_questions,
            "ai_provider_recognized_in": result.summary.ai_provider_recognized_in,
        },
    }

    metadata: Dict[str, object] = {
        "generated_at": result.generated_at.isoformat(),
        "models_run": result.models_run,
    }
    if result.metadata:
        metadata.update(
            {
                "source_url": result.metadata.source_url,
                "client_name": result.metadata.client_name,
                "provider_name": result.metadata.provider_name,
            }
        )
    payload["metadata"] = metadata
    return payload


def write_result(result: VisibilityResult, path: Path) -> Path:
    """Persist the serialized result to disk."""

    payload = serialize_result(result)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


__all__ = ["serialize_result", "write_result"]
