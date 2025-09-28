"""Command line entry point for the visibility agent prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common.config import load_settings
from src.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a visibility report from a transcript.")
    parser.add_argument("input", type=Path, help="Path to the transcript to ingest.")
    parser.add_argument("--story-id", dest="story_id", help="Identifier for the story or campaign.")
    parser.add_argument("--source-url", dest="source_url", help="Optional source URL for the story.")
    parser.add_argument("--client-name", dest="client_name", help="Client name referenced in the story.")
    parser.add_argument(
        "--provider-name",
        dest="provider_name",
        help="Name of the AI provider that should be masked and evaluated (defaults from env).",
    )
    parser.add_argument(
        "--provider-alias",
        dest="provider_aliases",
        action="append",
        default=None,
        help="Additional aliases for the provider (use multiple times).",
    )
    parser.add_argument(
        "--mode",
        choices=["stub", "live"],
        help="Force stub or live execution (defaults from env).",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Override model list for question answering (optional).",
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

    settings = load_settings()
    provider_name = args.provider_name or settings.provider.name
    provider_aliases = args.provider_aliases or settings.provider.aliases

    text = args.input.read_text(encoding="utf-8")
    result = run_pipeline(
        text=text,
        provider_name=provider_name,
        provider_aliases=provider_aliases,
        mode=args.mode,
        story_id=args.story_id,
        client_name=args.client_name,
        source_url=args.source_url,
        models_override=args.models,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return args.output


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    output_path = run_cli(args)
    print(json.dumps({"output": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
