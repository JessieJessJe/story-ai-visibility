"""Model runner abstraction for the visibility agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from src.common.config import Settings
from src.common.openai_client import OpenAIClient
from src.common.types import ClarifyingQuestion, QuestionAnswer


@dataclass
class ModelResponse:
    """Wrap raw content returned by a model."""

    content: str
    tokens_used: int = 0


class ModelRunner:
    """Execute model calls with optional live OpenAI integration."""

    def __init__(self, settings: Settings, client: OpenAIClient | None = None) -> None:
        self.settings = settings
        self.mode = settings.model.mode.lower()
        self._client = client
        self._calls_made = 0
        self._call_budget = settings.model.call_budget
        if self.is_live and self._client is None:
            self._client = OpenAIClient.from_model_settings(settings.model)

    @property
    def is_live(self) -> bool:
        return self.mode == "live"

    def invoke(self, messages: List[Dict[str, str]]) -> ModelResponse:
        """Invoke the primary model with arbitrary messages."""

        combined = "\n\n".join(message.get("content", "") for message in messages)
        if self.is_live:
            self._register_call()
            assert self._client is not None  # for type checkers
            response = self._client.chat(
                model=self.settings.model.name,
                messages=messages,
                temperature=self.settings.model.temperature,
                max_tokens=self.settings.model.max_output_tokens,
                reasoning_effort=self.settings.model.reasoning_effort,
                max_reasoning_tokens=self.settings.model.max_reasoning_tokens,
            )
            content = self._extract_content(response)
            tokens = len(content.split())
            return ModelResponse(content=content, tokens_used=tokens)
        return ModelResponse(content=f"[stub-response]\n{combined}", tokens_used=len(combined.split()))

    def answer_questions(
        self,
        model_name: str,
        questions: Iterable[ClarifyingQuestion],
        *,
        transcript: str | None = None,
        system_prompt: str = "",
    ) -> List[QuestionAnswer]:
        """Generate answers for each question using the requested model."""

        answers: List[QuestionAnswer] = []
        for index, question in enumerate(questions, start=1):
            if self.is_live:
                answer_text = self._answer_live(
                    model_name=model_name,
                    question=question,
                    transcript=transcript or "",
                    system_prompt=system_prompt,
                )
            else:
                answer_text = self._fabricate_answer(question)
                self._register_call()
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

    def _answer_live(
        self,
        *,
        model_name: str,
        question: ClarifyingQuestion,
        transcript: str,
        system_prompt: str,
    ) -> str:
        if self._client is None:
            raise RuntimeError("Live model invocation requested without an OpenAI client.")
        if not system_prompt:
            raise ValueError("System prompt is required for live model execution.")
        self._register_call()
        user_content = (
            "Transcript:\n"
            f"{transcript}\n\n"
            "Question:\n"
            f"{question.prompt}\n\n"
            "Respond concisely in 3 sentences or fewer."
        )
        response = self._client.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=self.settings.model.temperature,
            max_tokens=self.settings.model.max_output_tokens,
            reasoning_effort=self.settings.model.reasoning_effort,
            max_reasoning_tokens=self.settings.model.max_reasoning_tokens,
        )
        return self._extract_content(response)

    def _register_call(self) -> None:
        if self._call_budget is not None and self._calls_made >= self._call_budget:
            raise RuntimeError("Model call budget exceeded for this run.")
        self._calls_made += 1

    @staticmethod
    def _fabricate_answer(question: ClarifyingQuestion) -> str:
        prompt = question.prompt.lower()
        if question.kind == "masked_client":
            return "OpenAI is the likely provider powering this outcome."
        if "which ai providers" in prompt:
            return "OpenAI and similar vendors deliver this capability."
        return "The transcript lacks enough detail to determine the provider."

    @staticmethod
    def _extract_content(response: Any) -> str:
        if isinstance(response, dict):
            if response.get("status") == "incomplete":
                details = response.get("incomplete_details", {})
                model_name = response.get("model", "unknown-model")
                print(
                    f"[visibility] Warning: {model_name} response incomplete -> {details}",
                    flush=True,
                )
            if "output_text" in response:
                text = str(response.get("output_text", "")).strip()
                if text:
                    return text
            choices = response.get("choices")
            if isinstance(choices, list) and choices:
                message = choices[0].get("message", {})
                if isinstance(message, dict):
                    content = message.get("content")
                    text = ModelRunner._normalize_content(content)
                    if text:
                        return text
        if hasattr(response, "choices"):
            choices = getattr(response, "choices")
            if choices:
                first = choices[0]
                if isinstance(first, dict):
                    message = first.get("message", {})
                    if isinstance(message, dict):
                        text = ModelRunner._normalize_content(message.get("content"))
                        if text:
                            return text
                else:
                    message = getattr(first, "message", None)
                    if message is not None:
                        text = ModelRunner._normalize_content(getattr(message, "content", None))
                        if text:
                            return text
        return str(response).strip()

    @staticmethod
    def _normalize_content(content: Any) -> str:
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text") or item.get("content") or ""
                    if isinstance(text, str):
                        parts.append(text)
            return "".join(parts).strip()
        return ""


__all__ = ["ModelRunner", "ModelResponse"]
