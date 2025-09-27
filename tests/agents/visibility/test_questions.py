from src.agents.visibility.pillars import extract_pillars
from src.agents.visibility.questions import generate_questions


TRANSCRIPT = (
    "Engagement increased after the weekly evaluations. Feedback loops accelerated trust. Adoption momentum builds."
)


def test_generate_questions_creates_two_per_pillar() -> None:
    pillars = extract_pillars(TRANSCRIPT, target_count=2)
    questions = generate_questions(pillars)
    assert len(questions) == 4
    kinds = [question.kind for question in questions]
    assert kinds.count("masked_client") == 2
    assert kinds.count("industry_general") == 2
    for question in questions:
        assert question.prompt
        assert question.assumptions
        assert question.identifier


def test_generate_questions_returns_default_when_empty() -> None:
    questions = generate_questions([])
    assert len(questions) == 1
    assert questions[0].kind == "discovery_baseline"
    assert questions[0].identifier == "fallback_q1"
