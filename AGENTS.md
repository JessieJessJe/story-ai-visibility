# Repository Guidelines

## Project Structure & Module Organization
Runtime code lives in `src/agents/visibility/` with shared helpers (config, text, types) under `src/common/`. Prompts and templates are tracked in `assets/visibility/`, while specs and samples sit inside `docs/`. Tests mirror runtime paths under `tests/agents/visibility/`, and text fixtures reside in `tests/fixtures/`. Utility scripts (formatting, QA) belong in `scripts/`.

## Build, Test, and Development Commands
Use the built-in Python toolchain (3.11+)—no external services needed in stub mode. Run `python3 -m pytest` or `scripts/run_checks.sh` for the default quality gate. Execute the visibility workflow via `python3 -m src.cli --provider-name OpenAI --source-url https://… tests/fixtures/bluej_raw.txt` to generate a JSON report under `artifacts/`. Output captures per-model responses (GPT-5 primary plus GPT-4o comparison) for every question.

For live OpenAI calls export `MODEL_MODE=live`, `OPENAI_API_KEY=<key>`, and optionally `OPENAI_ORG`. The pipeline uses GPT-5 for extraction/questions and compares GPT-5 vs GPT-4o during the visibility check.

## Coding Style & Naming Conventions
Follow Black-style formatting with a 100-character line length and four-space indentation. Modules and variables use `snake_case`, classes use `PascalCase`, constants are `UPPER_SNAKE`. Add docstrings or inline comments only when logic is non-obvious (e.g., heuristics in pillar extraction). Prefer pure, side-effect-light functions to keep unit tests focused.

## Testing Guidelines
Tests live alongside their modules and rely on a lightweight pytest shim (`python3 -m pytest`). Cover ingestion masking, pillar extraction heuristics, question generation, model stubs, evaluation math, storage serialization, and CLI flow. Provide deterministic fixtures (e.g., `tests/fixtures/bluej_raw.txt`) so results stay reproducible. Aim for ≥85% branch coverage and keep golden JSON outputs in `artifacts/` when debugging.

## Commit & Pull Request Guidelines
Adopt Conventional Commits: `feat: add evaluator scoring` or `fix: tighten provider audit`. Each PR must include a summary, linked issue, and the output of `scripts/run_checks.sh`. When report aesthetics change, attach the generated JSON result for reviewers. Secure a second maintainer review before merging.

## Security & Configuration Tips
Never commit live secrets—`.env` is ignored and `.env.example` holds safe defaults. Configuration flows through `src/common/config.py`, while `load_story_document` enforces provider masking before anything leaves ingestion. When `MODEL_MODE=live`, `ModelRunner` routes through `OpenAIClient`, which applies retry/backoff, call-budget enforcement (16 calls/run by default), and avoids logging prompt content. Check artifacts for accidental provider leaks before uploading and rotate any mock credentials quarterly.
