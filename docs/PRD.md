# **Brand Visibility Test — PRD**

## **1\. Goal & Context**

The **Brand Visibility Test** measures whether large language models (LLMs) can recall or infer a specific AI provider when its name is masked from **success-story style blog posts**.

These stories highlight partnerships between an AI vendor and a business client. They are structured around *selling points* that matter to industry leaders — e.g., domain expertise, trust at scale, or rigorous evaluations.

The system masks the AI provider’s name and asks carefully framed **domain-expert questions** tied to those selling points. If the LLM still identifies the provider, that demonstrates brand visibility inside the model’s knowledge.

---

## **2\. Flow**

1. **Input**: A success story blogpost drawn from approved sources (e.g., OpenAI Stories export or partner-submitted briefing). Capture `source_url` for audit.

2. **Auto-extract selling points**: The system identifies \~3 key pillars. User can edit/approve.

3. **Generate questions**: For each selling point, create:

   * One question with the **client’s name masked**.

   * One **industry-general question** with no client reference.  
      → 3 selling points \= 6 questions.

4. **Mask AI provider**: Replace all occurrences of the AI vendor with `[MASK]`.

5. **Run**: Provide masked excerpt \+ 6 questions to GPT-4o and GPT-5 (one deterministic run per model → 12 total completions). Models are configurable via environment.

6. **Evaluate**: Check if the model names the masked AI provider. Aggregate detections per question across all models and rerun a keyword scan against answers before scoring.

7. **Output**: Structured JSON with answers \+ visibility summary.

---

## **2.1 Success Metrics & Guardrails**

- **Provider detection precision** ≥ 0.9 across the two-model ensemble (false positives < 5%).

- **Latency**: End-to-end run (masking → evaluation) finishes in under 4 minutes for a 1.5k word story.

- **Mask integrity**: Automated scan confirms 0 occurrences of the provider string in prompts or answers before scoring.

- **Analyst review load**: < 2 minutes of manual edits per story (pillar tweaks + mask spot-check).

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

`{`  
  `"story_id": "bluej-001",`  
  `"selling_points": [`  
    `{`  
      `"pillar": "Domain expertise",`  
      `"questions": [`  
        `{`  
          `"id": "sp1_q1_masked_client",`  
          `"answer": "OpenAI",`  
          `"ai_provider_inferred": true`  
        `},`  
        `{`  
          `"id": "sp1_q2_industry_general",`  
          `"answer": "Vendors like OpenAI",`  
          `"ai_provider_inferred": true`  
        `}`  
      `]`  
    `},`  
    `{`  
      `"pillar": "Trust through feedback",`  
      `"questions": [`  
        `{`  
          `"id": "sp2_q1_masked_client",`  
          `"answer": "OpenAI",`  
          `"ai_provider_inferred": true`  
        `},`  
        `{`  
          `"id": "sp2_q2_industry_general",`  
          `"answer": "OpenAI because of reliable feedback integration",`  
          `"ai_provider_inferred": true`  
        `}`  
      `]`  
    `},`  
    `{`  
      `"pillar": "Rigorous evaluations",`  
      `"questions": [`  
        `{`  
          `"id": "sp3_q1_masked_client",`  
          `"answer": "OpenAI",`  
          `"ai_provider_inferred": true`  
        `},`  
        `{`  
          `"id": "sp3_q2_industry_general",`  
          `"answer": "OpenAI is known for high benchmark performance",`  
          `"ai_provider_inferred": true`  
        `}`  
      `]`  
    `}`  
  `],`  
  `"summary": {`  
    `"total_questions": 6,`  
    `"ai_provider_recognized_in": 6`  
  `}`  
`}`

---

# **5\) System Architecture**

## **5.1 Architectural Pattern**

A modular, service-oriented pipeline with four core services:

1. **Ingestion & Masking Service**

   * Normalizes a success-story blogpost to plain text.

   * Applies **global AI-provider masking** (e.g., “OpenAI” → `[MASK]` across the entire context).

   * Runs a post-mask audit (case-insensitive keyword + embedding similarity) before prompts leave the service.

   * Supports **ephemeral client masking** for the *masked-client* question variant (only within that question’s prompt context).

   * Handles basic PII scrub (optional).

2. **Pillar & Question Service**

   * **Auto-extracts selling points (pillars)** via an LLM prompt (then stores for user review/edit).

   * **Generates 2 questions per pillar** in domain-expert language:

     * Q1: masked-client variant.

     * Q2: industry-general variant.

   * Ensures questions avoid “guess the blank” phrasing and anchor to capabilities, reliability, and evaluation posture.

3. **Model Runner Service**

   * Executes **one run per model** (GPT-4o, GPT-5) with:

     * Masked story excerpt (provider masked globally).

     * Six questions (2 per pillar), inserting the ephemeral client mask for the Q1 variants.

   * Uses consistent system prompts and deterministic sampling settings configurable per model.

4. **Evaluation & Reporting Service**

   * Parses answers and flags whether the **AI provider was inferred**.

   * Detects whether answers echo the **story’s reliability signals** tied to each pillar (e.g., “cited answers,” “feedback disagree rate,” “350+ prompt suite”).

   * Emits **structured JSON** \+ optional dashboard view.

---

## **5.2 Components & Responsibilities**

| Component | Tech/Interface | Responsibility |
| ----- | ----- | ----- |
| **API Gateway** | REST (JSON) | Receives story text; orchestrates the pipeline (idempotent runs). |
| **Ingestion & Masking** | Worker / Library | Normalization (HTML→text), global AI-provider masking, optional client ephemeral masking helper. |
| **Pillar Extractor** | LLM call \+ heuristics | Extracts 2–4 concise selling points with short rationales (user-editable). |
| **Question Generator** | LLM call \+ templates | Produces 2 questions per pillar, conforms to domain-expert tone; validates length/banlist. |
| **Prompt Assembler** | Library | Builds final prompts per model with system \+ user content, injects ephemeral client mask for Q1s. |
| **Model Runner** | OpenAI API | Runs GPT-4o and GPT-5 once each; captures raw and parsed answers. |
| **Evaluator** | Library | NER/regex/LLM-judge hybrid to detect **AI provider mentions** and **reliability signal echoes**. |
| **Storage** | SQLite / Postgres | Stories, pillars, questions, runs, answers, and summaries. |
| **Admin UI** (optional) | Web | Edit pillars; preview questions; run tests; view JSON results. |
| **Observability** | Logs/metrics | Latency, token usage, model outcomes, masking coverage %, error traces. |

---

## **5.3 Sequence (Happy Path)**

`sequenceDiagram`  
  `participant C as Client`  
  `participant API as API Gateway`  
  `participant IM as Ingestion & Masking`  
  `participant PX as Pillar Extractor`  
  `participant QG as Question Generator`  
  `participant MR as Model Runner`  
  `participant EV as Evaluator`  
  `participant DB as Storage`

  `C->>API: POST /run (story_text)`  
  `API->>IM: Normalize + mask AI provider globally`  
  `IM-->>API: masked_story`  
  `API->>PX: Extract selling points (auto)`  
  `PX-->>API: pillars[]`  
  `API->>DB: Save story + pillars (await user edit/confirm)`  
  `C->>API: PATCH /pillars (optional edits)`  
  `API->>QG: Generate 2 questions per pillar`  
  `QG-->>API: questions[]`  
  `API->>MR: Run GPT-4o (masked_story + questions)`  
  `MR-->>API: answers_4o`  
  `API->>MR: Run GPT-5 (masked_story + questions)`  
  `MR-->>API: answers_5`  
  `API->>EV: Evaluate (provider_inferred, signals_detected)`  
  `EV-->>API: evaluation_summary`  
  `API->>DB: Persist run, answers, summary`  
  `API-->>C: JSON results`

---

## **5.4 Data Model (Relational Sketch)**

**stories**

* `story_id` (pk)

* `source_title`, `source_url` (nullable)

* `raw_text`, `masked_text`

* `ai_provider_masked`: boolean (default true)

* `client_name`: text (if present in story)

* Timestamps

**pillars**

* `pillar_id` (pk), `story_id` (fk)

* `title` (short selling point)

* `rationale` (1–2 sentences)

* `status` (`auto_extracted` | `edited`)

**questions**

* `question_id` (pk), `pillar_id` (fk)

* `kind` (`masked_client` | `industry_general`)

* `text`

* `requires_client_mask`: boolean

**runs**

* `run_id` (pk), `story_id` (fk)

* `models` (array or join table)

* `status` (`completed`/`failed`)

* Timestamps

**answers**

* `answer_id` (pk), `run_id` (fk), `question_id` (fk), `model`

* `raw_answer`

* `ai_provider_inferred`: boolean

* `signals_detected`: jsonb (e.g., `["citations","feedback_rate","prompt_suite"]`)

**summaries**

* `run_id` (pk, fk)

* `total_questions`, `ai_provider_recognized_in` (int)

* `by_pillar`: jsonb (per-pillar counts)

---

## **5.5 Core APIs (MVP)**

* **POST `/api/visibility/run`**

  * Body: `{ "story_text": "...", "client_name": "Blue J" }`

  * Behavior: runs full pipeline (auto-extract pillars → question gen → model calls → evaluate).

  * Response: structured JSON (answers \+ summary).

* **POST `/api/visibility/extract-pillars`** (optional, for stepwise UX)

  * Body: `{ "story_text": "..." }`

  * Response: `{ "pillars": [...] }`

* **PATCH `/api/visibility/pillars/:story_id`**

  * Body: edited pillars array (user-approved).

  * Response: saved pillars.

* **POST `/api/visibility/generate-questions`**

  * Body: `{ "story_id": "...", "pillars": [...] }`

  * Response: `{ "questions": [...] }`

* **POST `/api/visibility/run-models`**

  * Body: `{ "story_id": "...", "questions": [...] }`

  * Response: `{ "answers": {...}, "summary": {...} }`

*(You can expose only `/run` for a one-click experience and keep the others internal.)*

