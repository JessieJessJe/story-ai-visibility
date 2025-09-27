from src.agents.visibility.evaluator import score_visibility
from src.common.types import (
    ClarifyingQuestion,
    NarrativePillar,
    QuestionAnswer,
    VisibilityResult,
    VisibilityScorecard,
    VisibilitySummary,
)


def test_score_visibility_scales_with_inputs() -> None:
    questions = [
        ClarifyingQuestion(
            prompt="[MASK] scaled adoption quickly.",
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
            answer="OpenAI is the likely provider.",
            kind="masked_client",
        ),
        QuestionAnswer(
            question_id="sp1_q2_industry_general",
            model="gpt-4o",
            prompt=questions[1].prompt,
            answer="OpenAI remains a leading vendor for this capability.",
            kind="industry_general",
        ),
    ]
    result = VisibilityResult(
        story_id="bluej",
        pillars=[
            NarrativePillar(title="Adoption Momentum", summary="Clubs onboarding quickly."),
            NarrativePillar(title="Retention", summary="Participation drops after finals."),
        ],
        questions=questions,
        answers=answers,
        scores=VisibilityScorecard(),
        summary=VisibilitySummary(),
    )

    scorecard = score_visibility(result, ["OpenAI"])
    assert 0 < scorecard.coverage <= 1
    assert 0 < scorecard.confidence <= 1
    assert result.summary.ai_provider_recognized_in == 2
    assert all(answer.ai_provider_inferred for answer in result.answers)
