from src.agents.visibility.model_runner import ModelRunner
from src.common.config import load_settings
from src.common.types import ClarifyingQuestion


def test_model_runner_echoes_messages() -> None:
    runner = ModelRunner(load_settings())
    response = runner.invoke([
        {"role": "system", "content": "Act as a strategist."},
        {"role": "user", "content": "Provide insights."},
    ])
    assert "[stub-response]" in response.content
    assert response.tokens_used > 0


def test_answer_questions_returns_structured_answers() -> None:
    runner = ModelRunner(load_settings())
    questions = [
        ClarifyingQuestion(
            prompt="[MASK] reports escalating adoption.",
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
    answers = runner.answer_questions("gpt-4o", questions)
    assert len(answers) == 2
    assert answers[0].question_id == "sp1_q1_masked_client"
    assert answers[0].answer
    assert answers[0].model == "gpt-4o"
