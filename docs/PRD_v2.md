Brand Visibility Test — Backend (FastAPI) PRD
Context

This system measures whether LLMs can recall or infer a masked AI provider from success-story blog posts.
The frontend (separate repo, Next.js + shadcn/ui) will provide a simple flow:

User pastes a blog post.

User clicks Analyze.

FE shows a progress placeholder until results return.

FE renders the final JSON (pillars, questions, model answers).

The backend (this repo) wraps the existing CLI pipeline in a FastAPI service, exposing one endpoint: POST /analyze.

Endpoint Contract
Path

POST /analyze

Request Body
{
  "text": "full blog post string",
  "provider_name": "OpenAI",                // optional
  "provider_aliases": ["Open AI","ChatGPT"] // optional
}


text: required — the blog post content to analyze.

provider_name: optional — canonical AI vendor name.

provider_aliases: optional — array of alternate strings to mask (nicknames, product names, etc.).

Defaults if omitted:

provider_name: "OpenAI" (from env OPENAI_PROVIDER_NAME)

provider_aliases: ["OpenAI","Open AI","OpenAI, Inc.","ChatGPT","GPT-4o","GPT-5","Sora","DALL·E"] (from env OPENAI_PROVIDER_ALIASES, JSON list)

Response Body
{
  "story_id": "story-abc123",
  "metadata": {
    "client_name": "Oscar",
    "provider_name": "OpenAI",
    "models_run": ["gpt-4o","gpt-5"],
    "mode": "live"
  },
  "summary": {
    "total_questions": 6,
    "ai_provider_recognized_in": 4
  },
  "selling_points": [
    {
      "pillar": "Domain expertise",
      "summary": "Known for deep expertise in X",
      "questions": [
        {
          "id": "q1",
          "prompt": "How does [MASK] demonstrate domain expertise?",
          "category": "domain",
          "kind": "masked-client",
          "responses": [
            {
              "model": "gpt-4o",
              "answer": "They show domain expertise by …",
              "ai_provider_inferred": true
            },
            {
              "model": "gpt-5",
              "answer": "Provider demonstrates expertise through …",
              "ai_provider_inferred": false
            }
          ]
        }
      ]
    }
  ]
}

Additional Requirements
Execution Mode

If OPENAI_API_KEY present: run in live mode.

If absent: run in stub mode (return fixture JSON).

Optional override: request may include "mode": "stub" | "live". If "live" requested without key, return 400.

Always echo metadata.mode in the response.

Story ID

If request includes story_id, echo it back.

Otherwise generate a deterministic ID: "story-" + sha1(text)[:10].

Timeout

Blocking request is acceptable in v0.

Allow up to 180s per request.

If exceeded, return { "code": "TIMEOUT", "message": "Pipeline exceeded 180s", "mode": "live" } with 504 status.

Health Check

GET /health → { "ok": true }

CORS

Enable CORS for:

http://localhost:3000 (FE dev)

Vercel FE prod domain (to be added later)

Deployment

Platform: Railway (preferred)

Dockerfile: Python slim image, install requirements, run uvicorn on port 8080.

Deliverable: public URL, e.g.
https://brand-vis-api.up.railway.app/analyze

Guardrails for Codex

Do not rename or restructure fields beyond this contract.

Do not truncate answers — return full text.

Do not introduce auth, DB persistence, or SSE in v0.

Keep pipeline logic in a callable run_pipeline(text: str, provider_name: str, provider_aliases: list[str], mode: str) -> dict.