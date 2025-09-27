from src.agents.visibility.pillars import extract_pillars, merge_pillars
from src.common.types import NarrativePillar


TRANSCRIPT = (
    "BlueJ expanded its pilot to three campuses, accelerating adoption momentum across student clubs.\n\n"
    "Feedback loops capture every bug report, enabling trust through quality improvements week over week.\n\n"
    "A 350 prompt evaluation suite benchmarks accuracy and clarity across jurisdictions.\n\n"
    "Monetization experiments lag while alumni upgrades stall."
)


def test_extract_pillars_generates_keyword_titles() -> None:
    pillars = extract_pillars(TRANSCRIPT, target_count=3)
    assert len(pillars) == 3
    titles = {pillar.title for pillar in pillars}
    assert "Adoption Momentum" in titles
    assert "Trust Through Feedback" in titles
    assert any("Rigorous" in title for title in titles)
    for pillar in pillars:
        assert pillar.summary
        assert pillar.evidence


def test_merge_pillars_preserves_priority() -> None:
    pillars = extract_pillars(TRANSCRIPT, target_count=3)
    duplicate = NarrativePillar(
        title=pillars[0].title,
        summary=pillars[0].summary,
        evidence=pillars[0].evidence,
        priority=5,
    )
    merged = merge_pillars(pillars + [duplicate])
    assert len(merged) == len(pillars)
    assert merged[0].priority == 1
