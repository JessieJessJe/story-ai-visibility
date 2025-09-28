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
            mode=None,
            output=output_path,
        )
        result_path = run_cli(args)
        payload = json.loads(result_path.read_text())
        assert payload["story_id"] == "bluej-001"
        assert payload["summary"]["total_questions"] == 6
        assert payload["summary"]["ai_provider_recognized_in"] >= 6
        models_run = payload["metadata"]["models_run"]
        assert "gpt-5" in models_run
        assert "gpt-4o" in models_run
        first_question = payload["selling_points"][0]["questions"][0]
        response_models = {resp["model"] for resp in first_question["responses"]}
        assert {"gpt-5", "gpt-4o"}.issubset(response_models)
