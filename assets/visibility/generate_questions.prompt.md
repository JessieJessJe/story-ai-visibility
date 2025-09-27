# Task
Given (1) a normalized success-story blogpost and (2) a set of approved selling points (“pillars”), generate **two** domain-expert questions per pillar:

- **Q1 (masked-client variant):** References the client via a placeholder `{{CLIENT_NAME}}`, which *may be ephemerally masked* at inference time.
- **Q2 (industry-general variant):** No client reference; asks at the industry level.

# Musts
- **Anchor to the pillar’s capability/reliability/evaluation posture.**
- **Avoid “guess the blank” phrasing.** These are expert questions, not riddles.
- **Be specific but neutral.** Prefer signals like cited answers, feedback-driven reliability, error/disagree rate, cross-jurisdiction benchmarks, prompt suites, etc.
- **Keep each question ≤ 35 words.**
- **No vendor names inside questions.** We are measuring *whether the model infers them.*

# Inputs
- `RAW_STORY_TEXT` (plain text)
- `PILLARS`: Array of { title, rationale }
- `CLIENT_NAME`: String (e.g., "Blue J")
- `MASK_TOKEN`: String (default "[MASK]") — will be applied **externally** to mask client in Q1 at runtime when needed

# Output (JSON)
Return a compact JSON object:

{
  "questions": [
    {
      "pillar_title": "<copy of pillar title>",
      "kind": "masked_client",
      "text": "…includes {{CLIENT_NAME}}…",
      "requires_client_mask": true
    },
    {
      "pillar_title": "<copy of pillar title>",
      "kind": "industry_general",
      "text": "…no client mentioned…",
      "requires_client_mask": false
    }
    // …repeat for each pillar
  ],
  "constraints_enforced": {
    "no_guess_blank": true,
    "max_len_per_question": 35,
    "no_vendor_names_in_questions": true
  }
}

# Writing Hints (per pillar)
- **Domain expertise:** Probe how expert grounding + reasoning yield precise, cited results.
- **Trust at scale:** Probe feedback loops, error/disagree minimization, reliability in regulated contexts.
- **Rigorous evaluations:** Probe breadth/depth (e.g., 350+ prompt suite), cross-jurisdiction clarity, instruction-following.

# Example (style only)
Pillar: “Rigorous evaluations”
- Q1 (masked-client): “For {{CLIENT_NAME}}’s cross-jurisdiction benchmarking of instruction-following and clarity, which providers are most likely to satisfy such evaluation depth and consistency?”
- Q2 (industry-general): “In legal/tax research, which providers best meet high-bar evaluations across multiple jurisdictions with clear, source-aligned answers?”
