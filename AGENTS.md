# Repository Guidelines

## Project Structure & Module Organization
Organize runtime code under `src/agents/<agent_name>` with shared utilities in `src/common/`. Narrative assets such as prompt templates and YAML story beats belong in `assets/`, while diagrams live in `docs/`. Tests mirror modules in `tests/agents/` (e.g., `tests/agents/test_storyteller.py`) and fixtures in `tests/fixtures/`.

## Build, Test, and Development Commands
Use `poetry install` to resolve dependencies and `poetry shell` for a locked virtualenv. Run the CLI locally via `poetry run python -m src.cli --story stories/example.yaml`. Quality gates: `poetry run ruff check src tests`, `poetry run black src tests`, and `poetry run pytest -q` for suites.

## Coding Style & Naming Conventions
Target Python 3.11, four-space indentation, and exhaustive type hints. Name modules in snake_case (`story_branching.py`), classes in PascalCase, constants uppercase. Keep public functions documented with short docstrings explaining branching logic; prefer pure helpers under 40 lines.

## Testing Guidelines
Pytest powers validation; co-locate tests with their subject using `test_<module>.py`. Exercise every narrative branch with parametrized tests and stash reusable prompts under `tests/fixtures/`. Maintain ≥85% branch coverage and record golden transcripts in `tests/data/`.

## Commit & Pull Request Guidelines
Adopt Conventional Commits already used in history (`feat: add bedtime branch`, `fix: reset narrator state`). PRs need a concise summary, linked issue, and `pytest` output; attach transcripts or screenshots when narrative flow changes. Request review from another agent maintainer before merge.

## Security & Configuration Tips
Store secrets in `.env` (ignored) and publish safe defaults in `.env.example`. Load configuration through `src/config.py` and sanitize transcripts before committing. Delete stale keys and rotate mock credentials quarterly.
