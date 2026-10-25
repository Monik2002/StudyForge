# AI pipeline

1. Bound note size.
2. Send notes as untrusted reference material to a configured Gemma model.
3. Request JSON output with question type, options, correct IDs, explanation, difficulty, tags and source excerpt.
4. Parse and validate supported type, option uniqueness, answer references, cardinality and explanation presence.
5. Persist as a draft.
6. Require human review and approval before an assessment.

Valid JSON is not proof of correctness. Keep model ID configurable and verify structured-output support for the exact model. Add semantic grounding checks, deduplication, benchmark evaluation and async jobs before production.
