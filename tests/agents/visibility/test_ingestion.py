from tempfile import TemporaryDirectory
from pathlib import Path

from src.agents.visibility.ingestion import (
    GLOBAL_MASK_TOKEN,
    audit_mask_integrity,
    load_story_document,
    load_transcript,
    mask_provider_terms,
    normalize_story_text,
)
from src.common.types import StoryMetadata

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def test_load_transcript_returns_clean_string() -> None:
    path = FIXTURES / "bluej_raw.txt"
    content = load_transcript(path)
    assert "\n\n" not in content
    assert "Oscar brings AI to health insurance" in content


def test_normalize_story_text_strips_markup() -> None:
    raw = "<p>BlueJ Campus Summit</p>\n\n<p>Launch update</p>"
    cleaned = normalize_story_text(raw)
    assert "<p>" not in cleaned
    assert "Launch update" in cleaned


def test_mask_provider_terms_applies_global_mask() -> None:
    content = "OpenAI delivered enterprise tooling for BlueJ."
    summary = mask_provider_terms(content, ["OpenAI"])
    assert GLOBAL_MASK_TOKEN in summary.masked_text
    assert "OpenAI" not in summary.masked_text
    assert not summary.issues


def test_audit_mask_integrity_reports_unmasked_terms() -> None:
    content = "OpenAI delivered enterprise tooling for BlueJ."
    issues = audit_mask_integrity(content, ["OpenAI"])
    assert issues
    assert "OpenAI" in issues[0]


def test_load_story_document_masks_and_validates() -> None:
    path = FIXTURES / "bluej_raw.txt"
    metadata = StoryMetadata(
        story_id="bluej",
        provider_name="OpenAI",
        source_url="https://openai.com/index/blue-j/",
        client_name="Blue J",
    )
    document = load_story_document(path, metadata)
    assert metadata.story_id == document.metadata.story_id
    assert "OpenAI" not in document.masked_text
    assert GLOBAL_MASK_TOKEN in document.masked_text


def test_load_story_document_raises_when_mask_fails() -> None:
    with TemporaryDirectory() as tmp_dir:
        raw_path = Path(tmp_dir) / "story.txt"
        raw_path.write_text("OpenAI remains visible", encoding="utf-8")
        metadata = StoryMetadata(story_id="story", provider_name="")

        try:
            load_story_document(raw_path, metadata)
        except ValueError as exc:
            assert "provider alias" in str(exc)
        else:  # pragma: no cover - defensive
            raise AssertionError("Expected masking failure for missing provider name")
