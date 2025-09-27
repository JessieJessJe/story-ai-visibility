"""Higher-level orchestration for GPT-driven visibility workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from src.agents.visibility import pillars as stub_pillars
from src.agents.visibility import questions as stub_questions
from src.agents.visibility.model_runner import ModelRunner
from src.agents.visibility.prompt_assembler import load_template, render_template
from src.common.config import Settings
from src.common.types import ClarifyingQuestion, NarrativePillar, StoryDocument

ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets" / "visibility"


class VisibilityLLMService:
    """Use GPT-5 (live mode) or heuristics (stub mode) to drive the workflow."""

    def __init__(self, settings: Settings, runner: ModelRunner | None = None) -> None:
        self.settings = settings
        self.runner = runner or ModelRunner(settings)
        self.system_prompt = load_template(ASSETS_DIR / "system.prompt.md")
        self.extract_template = load_template(ASSETS_DIR / "extract_pillars.prompt.md")
        self.questions_template = load_template(ASSETS_DIR / "generate_questions.prompt.md")

    @property
    def is_live(self) -> bool:
        return self.runner.is_live

    def extract_pillars(self, document: StoryDocument, target_count: int = 3) -> List[NarrativePillar]:
        if not self.is_live:
            return stub_pillars.extract_pillars(document.masked_text, target_count=target_count)

        user_prompt = render_template(self.extract_template, transcript=document.masked_text)
        response = self.runner.invoke(
            [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        data = self._parse_json(response.content)
        pillars_data = data.get("pillars", [])
        pillars: List[NarrativePillar] = []
        for index, item in enumerate(pillars_data, start=1):
            pillars.append(
                NarrativePillar(
                    title=item.get("title", f"Signal {index}"),
                    summary=item.get("summary", ""),
                    evidence=item.get("evidence", []),
                    priority=item.get("priority", index),
                )
            )
        if not pillars:
            return stub_pillars.extract_pillars(document.masked_text, target_count=target_count)
        return pillars[:target_count]

    def generate_questions(self, pillars: Iterable[NarrativePillar]) -> List[ClarifyingQuestion]:
        pillars_list = list(pillars)
        if not self.is_live:
            return stub_questions.generate_questions(pillars_list)

        payload = [
            {
                "index": index,
                "title": pillar.title,
                "summary": pillar.summary,
                "evidence": pillar.evidence,
            }
            for index, pillar in enumerate(pillars_list, start=1)
        ]
        user_prompt = render_template(self.questions_template, pillars_json=json.dumps(payload, ensure_ascii=False))
        response = self.runner.invoke(
            [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        data = self._parse_json(response.content)
        questions_data = data.get("questions", [])
        questions: List[ClarifyingQuestion] = []
        for item in questions_data:
            idx = item.get("pillar_index", len(questions) + 1)
            kind = item.get("kind", "industry_general")
            identifier = item.get("identifier") or self._identifier_from(idx, kind)
            questions.append(
                ClarifyingQuestion(
                    prompt=item.get("prompt", ""),
                    category=item.get("category", "discovery"),
                    kind=kind,
                    identifier=identifier,
                    assumptions=item.get("assumptions", []),
                )
            )
        if not questions:
            return stub_questions.generate_questions(pillars_list)
        return questions

    def build_answers(
        self,
        models: Iterable[str],
        questions: List[ClarifyingQuestion],
        *,
        transcript: str,
    ):
        all_answers = []
        for model_name in models:
            answers = self.runner.answer_questions(
                model_name,
                questions,
                transcript=transcript,
                system_prompt=self.system_prompt,
            )
            all_answers.extend(answers)
        return all_answers

    @staticmethod
    def _identifier_from(pillar_index: int, kind: str) -> str:
        suffix = "q1_masked_client" if "masked" in kind else "q2_industry_general"
        return f"sp{pillar_index}_{suffix}"

    @staticmethod
    def _parse_json(raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}


__all__ = ["VisibilityLLMService"]
