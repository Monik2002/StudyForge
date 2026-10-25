# StudyForge API

FastAPI backend for the StudyForge learning and assessment platform.

- Health check: `/health`
- Interactive OpenAPI: `/docs`
- API prefix: `/api/v1`

Install locally with `pip install -e ".[dev]"`. Set `DATABASE_URL`, `JWT_SECRET`, and the server-side `GEMINI_API_KEY` in the environment. `GEMMA_MODEL_ID` defaults to `gemma-4-26b-a4b-it` for question generation; `DOCUMENT_VISION_MODEL_ID` separately defaults to `gemini-2.5-flash` for PDF/image extraction. Both model IDs can be overridden for API keys with access to other supported models. Never expose the API key through a `NEXT_PUBLIC_` variable. The default SQLite URL is intended only for local smoke tests; Docker Compose uses PostgreSQL.
