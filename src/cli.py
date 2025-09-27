"""Command line entry point for the visibility agent prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.agents.visibility.evaluator import score_visibility
from src.agents.visibility.ingestion import load_story_document
from src.agents.visibility.model_runner import ModelRunner
from src.agents.visibility.service import VisibilityLLMService
from src.agents.visibility.storage import write_result
from src.common.config import load_settings
from src.common.types import (
    StoryMetadata,
    VisibilityResult,
    VisibilityScorecard,
    VisibilitySummary,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a visibility report from a transcript.")
    parser.add_argument("input", type=Path, help="Path to the transcript to ingest.")
    parser.add_argument("--story-id", dest="story_id", default="sample-story", help="Identifier for the story or campaign.")
    parser.add_argument("--source-url", dest="source_url", help="Optional source URL for the story.")
    parser.add_argument("--client-name", dest="client_name", help="Client name referenced in the story.")
    parser.add_argument(
        "--provider-name",
        dest="provider_name",
        required=True,
        help="Name of the AI provider that should be masked and evaluated.",
    )
    parser.add_argument(
        "--provider-alias",
        dest="provider_aliases",
        action="append",
        default=[],
        help="Additional aliases for the provider (use multiple times).",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Models to run against the masked story. Defaults to primary + comparison models.",
    )
    parser.add_argument(
        "--output",
        dest="output",
        type=Path,
        default=Path("artifacts/visibility.json"),
        help="Where to store the generated report.",
    )
    return parser


def run_cli(args: argparse.Namespace) -> Path:
    """Execute the pipeline and persist a visibility result."""

    metadata = StoryMetadata(
        story_id=args.story_id,
        source_url=args.source_url,
        client_name=args.client_name,
        provider_name=args.provider_name,
    )

    settings = load_settings()
    runner = ModelRunner(settings)
    service = VisibilityLLMService(settings, runner)

    document = load_story_document(
        args.input,
        metadata,
        provider_aliases=args.provider_aliases,
    )

    pillars = service.extract_pillars(document)
    questions = service.generate_questions(pillars)

    default_models = [settings.model.name, *settings.model.comparison_models]
    model_list = args.models or default_models
    # Remove duplicates while preserving order
    seen: set[str] = set()
    models: list[str] = []
    for model_name in model_list:
        if model_name in seen:
            continue
        seen.add(model_name)
        models.append(model_name)

    answers = service.build_answers(models, questions, transcript=document.masked_text)

    result = VisibilityResult(
        story_id=metadata.story_id,
        pillars=pillars,
        questions=questions,
        answers=answers,
        scores=VisibilityScorecard(),
        summary=VisibilitySummary(),
        models_run=models,
        metadata=metadata,
    )

    provider_aliases = [alias for alias in [metadata.provider_name, *(args.provider_aliases or [])] if alias]
    score_visibility(result, provider_aliases)

    output_path = write_result(result, args.output)
    return output_path


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    output_path = run_cli(args)
    print(json.dumps({"output": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
