# Operations

Local: copy `.env.example` to `.env`, set a strong JWT secret and Gemma API key, then `docker compose up --build`.

Production checklist:
- Managed secrets and separate provider keys per environment.
- HTTPS, strict CORS, request limits, generation quotas and rate limits.
- Reviewed Alembic migrations as release steps; do not rely on startup table creation.
- Metrics, redacted logs and error tracking.
- PostgreSQL backups and tested restore.
- Dependency/container scanning, rollout and rollback procedure.
- Verify model availability, API behavior, quotas and pricing.
