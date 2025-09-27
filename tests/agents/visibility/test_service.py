from pathlib import Path

from src.agents.visibility.ingestion import load_story_document
from src.agents.visibility.service import VisibilityLLMService
from src.common.config import load_settings
from src.common.types import StoryMetadata

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def test_service_stub_flow_produces_outputs() -> None:
    settings = load_settings()
    service = VisibilityLLMService(settings)
    metadata = StoryMetadata(
        story_id="bluej",
        provider_name="OpenAI",
        source_url="https://openai.com/index/blue-j/",
        client_name="Blue J",
    )
    document = load_story_document(FIXTURES / "bluej_raw.txt", metadata, provider_aliases=["OpenAI"])

    pillars = service.extract_pillars(document)
    assert len(pillars) >= 1

    questions = service.generate_questions(pillars)
    assert len(questions) >= 2

    answers = service.build_answers(["gpt-4o", "gpt-5"], questions, transcript=document.masked_text)
    assert answers
    assert all(answer.answer for answer in answers)
