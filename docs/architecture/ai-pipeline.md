# AI pipeline

1. Bound uploaded file and note sizes.
2. Extract text from supported files. PDF/image extraction, and embedded DOCX images, use the separate `DOCUMENT_VISION_MODEL_ID` (default `gemini-2.5-flash`); ordinary text extraction is local.
3. Save extracted notes and show the authenticated owner a preview before question generation. The user explicitly starts generation after reviewing the text.
4. Send notes as untrusted reference material to `GEMMA_MODEL_ID` (default `gemma-4-26b-a4b-it`) through the Google Gemini API.
5. Request JSON output with question type, options, correct IDs, explanation, difficulty, tags and source excerpt.
6. Parse and validate supported type, option uniqueness, answer references, cardinality and explanation presence.
7. Persist as a draft.
8. Require human review and approval before an assessment.

The backend uses the `google-genai` SDK's `models.generate_content` method with `response_mime_type="application/json"`, then parses and validates the returned questions before saving a draft. Provider failures return a sanitized error type and status without exposing provider response bodies or credentials. Valid JSON is not proof of correctness. Keep model IDs configurable and verify model access and structured-output support with the configured API key. Add semantic grounding checks, deduplication, benchmark evaluation and async jobs before production.
