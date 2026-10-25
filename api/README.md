# StudyForge API

FastAPI backend for the StudyForge learning and assessment platform.

- Health check: `/health`
- Interactive OpenAPI: `/docs`
- API prefix: `/api/v1`

Install locally with `pip install -e ".[dev]"`. Set `DATABASE_URL`, `JWT_SECRET`, `GEMINI_API_KEY`, and `GEMMA_MODEL_ID` in the environment. The default SQLite URL is intended only for local smoke tests; Docker Compose uses PostgreSQL.
