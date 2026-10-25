# AI pipeline

1. Bound note size.
2. Send notes as untrusted reference material to `GEMMA_MODEL_ID` (default `gemma-4-26b-a4b-it`) through the Google Gemini API. PDF/image extraction uses the separate `DOCUMENT_VISION_MODEL_ID` (default `gemini-2.5-flash`).
3. Request JSON output with question type, options, correct IDs, explanation, difficulty, tags and source excerpt.
4. Parse and validate supported type, option uniqueness, answer references, cardinality and explanation presence.
5. Persist as a draft.
6. Require human review and approval before an assessment.

The backend uses the `google-genai` SDK's `models.generate_content` method with `response_mime_type="application/json"`, then parses and validates the returned questions before saving a draft. Provider failures return a sanitized error type and status without exposing provider response bodies or credentials. Valid JSON is not proof of correctness. Keep model IDs configurable and verify model access and structured-output support with the configured API key. Add semantic grounding checks, deduplication, benchmark evaluation and async jobs before production.
