from datetime import datetime

from src.agents.visibility.storage import serialize_result
from src.common.types import (
    ClarifyingQuestion,
    NarrativePillar,
    QuestionAnswer,
    StoryMetadata,
    VisibilityResult,
    VisibilityScorecard,
    VisibilitySummary,
)


def build_result() -> VisibilityResult:
    pillars = [
        NarrativePillar(title="Adoption Momentum", summary="Clubs onboarding quickly."),
    ]
    questions = [
        ClarifyingQuestion(
            prompt="[MASK] reports accelerating adoption.",
            category="validation",
            kind="masked_client",
            identifier="sp1_q1_masked_client",
        ),
        ClarifyingQuestion(
            prompt="Across the market, which AI providers support adoption momentum?",
            category="discovery",
            kind="industry_general",
            identifier="sp1_q2_industry_general",
        ),
    ]
    answers = [
        QuestionAnswer(
            question_id="sp1_q1_masked_client",
            model="gpt-4o",
            prompt=questions[0].prompt,
            answer="OpenAI likely powers the deployment.",
            kind="masked_client",
            ai_provider_inferred=True,
        ),
        QuestionAnswer(
            question_id="sp1_q1_masked_client",
            model="gpt-5",
            prompt=questions[0].prompt,
            answer="GPT-5 confirms OpenAI enables the rollout.",
            kind="masked_client",
            ai_provider_inferred=True,
        ),
        QuestionAnswer(
            question_id="sp1_q2_industry_general",
            model="gpt-4o",
            prompt=questions[1].prompt,
            answer="OpenAI remains a leading vendor.",
            kind="industry_general",
            ai_provider_inferred=True,
        ),
    ]
    return VisibilityResult(
        story_id="bluej",
        pillars=pillars,
        questions=questions,
        answers=answers,
        scores=VisibilityScorecard(coverage=1.0, confidence=0.8),
        summary=VisibilitySummary(total_questions=2, ai_provider_recognized_in=2),
        generated_at=datetime(2024, 1, 1),
        models_run=["gpt-4o"],
        metadata=StoryMetadata(
            story_id="bluej",
            source_url="https://openai.com/index/blue-j/",
            client_name="Blue J",
            provider_name="OpenAI",
        ),
    )


def test_serialize_result_matches_schema_shape() -> None:
    result = build_result()
    payload = serialize_result(result)
    assert payload["story_id"] == "bluej"
    assert payload["summary"]["total_questions"] == 2
    responses = payload["selling_points"][0]["questions"][0]["responses"]
    assert len(responses) == 2
    assert responses[0]["ai_provider_inferred"] is True
    assert payload["metadata"]["source_url"] == "https://openai.com/index/blue-j/"
