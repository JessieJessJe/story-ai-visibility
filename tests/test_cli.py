import json
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory

from src.cli import run_cli

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "bluej_raw.txt"


def test_run_cli_produces_visibility_report() -> None:
    with TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "visibility.json"
        args = Namespace(
            input=FIXTURE,
            story_id="bluej-001",
            source_url="https://openai.com/index/blue-j/",
            client_name="Blue J",
            provider_name="OpenAI",
            provider_aliases=["OpenAI"],
            models=["gpt-4o", "gpt-5"],
            output=output_path,
        )
        result_path = run_cli(args)
        payload = json.loads(result_path.read_text())
        assert payload["story_id"] == "bluej-001"
        assert payload["summary"]["total_questions"] == 6
        assert payload["summary"]["ai_provider_recognized_in"] >= 6
        assert payload["metadata"]["models_run"] == ["gpt-4o", "gpt-5"]
