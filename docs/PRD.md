# **Brand Visibility Test — PRD**

## **1\. Goal & Context**

The **Brand Visibility Test** measures whether large language models (LLMs) can recall or infer a specific AI provider when its name is masked from **success-story style blog posts**.

These stories highlight partnerships between an AI vendor and a business client. They are structured around *selling points* that matter to industry leaders — e.g., domain expertise, trust at scale, or rigorous evaluations.

The system masks the AI provider’s name and asks carefully framed **domain-expert questions** tied to those selling points. If the LLM still identifies the provider, that demonstrates brand visibility inside the model’s knowledge.

---

## **2\. Flow**

1. **Input**: Provide a success-story transcript (fixtures for v0). Analysts pass `story_id`, optional `source_url`, `client_name`, and provider aliases.

2. **Mask provider**: `load_story_document` normalizes text and replaces provider aliases with `[MASK]` before prompting.

3. **Extract pillars (GPT-5)**: GPT-5 Responses API returns ~3 pillars (JSON); analysts can override. Stub mode falls back to heuristics.

4. **Generate questions (GPT-5)**: GPT-5 produces masked-client and industry-general questions per pillar (JSON). Stub mode mirrors schema.

5. **Run**: CLI calls GPT-5 (primary) and GPT-4o (comparison) with the masked transcript + questions. Defaults rely on env/flags and enforce a call budget (20 by default) plus retry/backoff safeguards.

6. **Evaluate**: Log per-model answers, flag provider detections, aggregate per question, and perform a keyword post-check on responses.

7. **Output**: Emit JSON artifact with pillars, questions, per-model `responses`, scores, and summary metrics.

---

## **2.1 Success Metrics & Guardrails**

- **Provider detection precision** ≥ 0.9 across the two-model ensemble (false positives < 5%).

- **Latency**: End-to-end run (masking → evaluation) finishes in under 4 minutes for a 1.5k word story.

- **Mask integrity**: Automated scan confirms 0 occurrences of the provider string in prompts or answers before scoring.

- **Analyst review load**: < 2 minutes of manual edits per story (pillar tweaks + mask spot-check).

- **Token budget**: Allocate ≥4096 completion tokens (and matching reasoning tokens when enabled) per GPT-5 call to avoid `status=incomplete` truncation.

---

## **3\. Example — Blue J Story**

[https://openai.com/index/blue-j/](https://openai.com/index/blue-j/)

### **Extracted Selling Points (from the blogpost)**

1. **Leverage domain expertise** to build a tax research solution no one else can.

2. **Scale trust through user feedback**, keeping error rates extremely low.

3. **Design evaluations that raise the bar**, benchmarking with 350+ prompts across jurisdictions.

---

### **Selling Point 1 — Domain Expertise**

* **Masked Client Question**

   “\[MASK\] built a tax research system grounded in deep domain expertise. Which AI provider’s models would power a system like this?”

* **Industry-General Question**

   “For AI systems in tax research, which providers are recognized for combining reasoning with authoritative sources to deliver cited answers?”

---

### **Selling Point 2 — Trust Through Feedback**

* **Masked Client Question**

   “\[MASK\] scaled trust by capturing user feedback and reducing the disagree rate to extremely low levels. Which AI provider is most likely enabling this reliability?”

* **Industry-General Question**

   “In regulated fields like tax law, which AI vendors are known for reliable performance when paired with strong human feedback loops?”

---

### **Selling Point 3 — Rigorous Evaluations**

* **Masked Client Question**

   “\[MASK\] benchmarked over 350 prompts across multiple jurisdictions to evaluate instruction-following, source alignment, and clarity. Which AI provider’s models fit this description?”

* **Industry-General Question**

   “When evaluating AI for legal and tax research, which vendors are recognized for meeting high standards on accuracy and clarity?”

---

## **4\. Output JSON Example**

```json
{
  "story_id": "oscar-live-005",
  "selling_points": [
    {
      "pillar": "Finding A Relevant",
      "summary": "Finding a relevant piece of information in a medical record is like finding a needle in a haystack...",
      "questions": [
        {
          "id": "sp1_q1_masked_client",
          "prompt": "[MASK] reports that...",
          "category": "validation",
          "kind": "masked_client",
          "responses": [
            {"model": "gpt-5", "answer": "OpenAI...", "ai_provider_inferred": true},
            {"model": "gpt-4o", "answer": "Unsure — evidence insufficient...", "ai_provider_inferred": false}
          ]
        },
        {
          "id": "sp1_q2_industry_general",
          "prompt": "Across the market, which AI providers...",
          "category": "discovery",
          "kind": "industry_general",
          "responses": [
            {"model": "gpt-5", "answer": "OpenAI; Google; Microsoft...", "ai_provider_inferred": true},
            {"model": "gpt-4o", "answer": "AI providers like OpenAI and Google...", "ai_provider_inferred": true}
          ]
        }
      ]
    }
  ],
  "summary": {"total_questions": 6, "ai_provider_recognized_in": 6},
  "scores": {"coverage": 1.0, "confidence": 0.9},
  "metadata": {"models_run": ["gpt-5", "gpt-4o"], "generated_at": "2025-09-27T21:43:54Z"}
}
```

---

# **5\) System Architecture**

## **5.1 Architectural Pattern**

This release ships as a CLI-first pipeline:

## **5.2 Key Components**

| Component | Implementation | Notes |
| --- | --- | --- |
| CLI Orchestrator | `src/cli.py` | Handles masking, prompt orchestration, artifact write. |
| GPT-5 Services | `VisibilityLLMService` + Responses API | Extract pillars, generate questions (JSON contract). |
| ModelRunner | `src/agents/visibility/model_runner.py` | GPT-5 via Responses, GPT-4o via Chat Completions; retry/backoff + call budget. |
| Evaluator | `src/agents/visibility/evaluator.py` | Aggregates detections, computes coverage/confidence. |
| Storage | Filesystem (`artifacts/`) | JSON artifact per run; no DB in v0. |
| Logging | CLI stdout | Warns on incomplete responses, surfaces errors. |

1. **CLI Orchestrator (`src/cli.py`)** – loads/masks transcripts, orchestrates GPT calls, writes artifacts.
2. **LLM Services (GPT-5 Responses)** – extract pillars and generate questions in JSON; stub heuristics mimic the contract for tests.
3. **ModelRunner** – GPT-5 via `responses.create`, GPT-4o via `chat.completions`, with retry/backoff and call-budget safeguards.
4. **Evaluator & Storage** – keyword-based provider detection, scoring, and filesystem persistence (`artifacts/`).

Future iterations may introduce REST APIs, persistent storage, and richer evaluation signals.

## **5.3 Workflow Summary (CLI Release)**

- Analyst runs `python3 -m src.cli <transcript> --provider-name <name> ...`.
- CLI loads and masks the transcript via `load_story_document`.
- GPT-5 Responses API extracts pillars (JSON). Stub heuristics mirror the schema in test mode.
- GPT-5 Responses API generates questions (JSON).
- For each configured model (GPT-5 primary + comparison list), ModelRunner calls OpenAI (Responses for GPT-5, Chat Completions for GPT-4o) with retry/backoff and call-budget safeguards.
- Evaluator aggregates provider detections per question and computes coverage/confidence scores.
- CLI logs any `status=incomplete` responses (e.g., token-cap hits) so analysts can adjust budgets or prompts.
- CLI writes `artifacts/<story_id>.json`, containing per-model responses for every question.

## **5.4 Artifact Structure**

See `docs/schema/visibility_result.json`. Each question includes a `responses` array (one entry per model), preserving GPT-5 and comparison outputs.

## **5.5 Future Extensions**

- Add REST API/Admin UI + persistent storage when the CLI pipeline stabilises.
- Extend evaluator to capture reliability signals (citations, feedback loops).
- Emit structured telemetry (latency, token totals, incomplete-response warnings).
