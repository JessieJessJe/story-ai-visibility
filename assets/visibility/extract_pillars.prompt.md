# Task
From a success-story blogpost, extract **2–4 concise selling points (“pillars”)** that matter to industry leaders evaluating AI providers.

# What qualifies as a pillar
Short, distinct claims that reflect:
- **Domain expertise** applied to the problem
- **Trust/reliability at scale**, often via feedback loops and low error/disagree rates
- **Rigorous evaluation** culture (prompt suites, cross-jurisdiction clarity, instruction-following)
- Any other high-signal evidence of capability, reliability, or evaluation posture present in the story

# Musts
- **Title:** ≤ 6 words, specific and non-fluffy
- **Rationale:** 1–2 sentences citing concrete evidence from the story (no vendor names)
- **No duplicates / no overlap.** Each pillar must be meaningfully distinct.
- **Order by importance** to the buyer persona implied by the story.

# Inputs
- `RAW_STORY_TEXT` (plain text)

# Output (JSON)
Return a compact JSON object:

{
  "pillars": [
    {
      "title": "…concise selling point…",
      "rationale": "…1–2 sentences grounded in the story…",
      "status": "auto_extracted"
    }
    // 2–4 items total
  ],
  "notes": {
    "extracted_from_story": true,
    "no_vendor_names": true
  }
}

# Quality Bar
- Prefer evidence such as: cited answers, expert workflows, human-in-the-loop improvements, measured error/disagree rates, benchmark sizes (e.g., 350+ prompts), cross-market/jurisdiction coverage.
- Avoid vague platitudes (“innovative”, “cutting-edge”) unless tied to measurable signals.
