"""Minimal model runner abstraction for the visibility agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from src.common.config import Settings
from src.common.types import ClarifyingQuestion, QuestionAnswer


@dataclass
class ModelResponse:
    """Wrap raw content returned by a model."""

    content: str
    tokens_used: int = 0


class ModelRunner:
    """Stubbed model runner that fabricates answers for local testing."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def invoke(self, messages: List[dict[str, str]]) -> ModelResponse:
        """Return a predictable response without calling a real provider."""

        combined = "\n\n".join(message.get("content", "") for message in messages)
        return ModelResponse(content=f"[stub-response]\n{combined}", tokens_used=len(combined.split()))

    def answer_questions(self, model_name: str, questions: Iterable[ClarifyingQuestion]) -> List[QuestionAnswer]:
        """Generate deterministic answers for each question."""

        answers: List[QuestionAnswer] = []
        for index, question in enumerate(questions, start=1):
            answer_text = self._fabricate_answer(question)
            identifier = question.identifier or f"q{index}_{question.kind}"
            answers.append(
                QuestionAnswer(
                    question_id=identifier,
                    model=model_name,
                    prompt=question.prompt,
                    answer=answer_text,
                    kind=question.kind,
                )
            )
        return answers

    @staticmethod
    def _fabricate_answer(question: ClarifyingQuestion) -> str:
        prompt = question.prompt.lower()
        if question.kind == "masked_client":
            return "OpenAI is the likely provider powering this outcome."
        if "which ai providers" in prompt:
            return "OpenAI and similar vendors deliver this capability."
        return "The transcript lacks enough detail to determine the provider."


__all__ = ["ModelRunner", "ModelResponse"]
