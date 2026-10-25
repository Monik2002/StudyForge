# Operations

Local: copy `.env.example` to `.env`, set a strong JWT secret and Gemma API key, then `docker compose up --build`.

## Vercel + Render + managed PostgreSQL

Do not provision a plan until you have reviewed its current price, limits, backup policy,
region, and sleep/scale behavior. Keep the database managed separately from the API
container and place it in the same region as the backend when possible.

1. Create a managed PostgreSQL database. Create a backup before connecting an existing
   database. Copy its private/internal connection URL for the backend; do not add it to
   Git or paste it into chat. The API normalizes `postgres://` and `postgresql://` URLs
   to the installed psycopg 3 driver and handles percent-encoded credentials.
2. In Render, create a Web Service from the GitHub repository. Set the service root
   directory to `api`, select the Docker runtime and `Dockerfile`, and choose the
   instance plan only after reviewing its cost. Set the health check path to `/health`.
   The container binds to `0.0.0.0:$PORT`; on production startup it runs
   `alembic upgrade head` before starting Uvicorn.
3. Set these backend environment variables in Render's dashboard:
   - `APP_ENV=production`
   - `DATABASE_URL` to the managed database's private connection URL
   - `JWT_SECRET` to a newly generated random secret of at least 32 characters
   - `JWT_EXPIRE_MINUTES=720`
   - `GEMINI_API_KEY` to the Google API key (backend only)
   - `GEMMA_MODEL_ID=gemma-4-26b-a4b-it`
   - `DOCUMENT_VISION_MODEL_ID=gemini-2.5-flash`
   - `API_CORS_ORIGINS` to the exact Vercel site origin, for example
     `https://your-studyforge.vercel.app` (no path, trailing slash, or wildcard)
   - `MAX_SOURCE_CHARS=100000`
   - `MAX_QUESTIONS_PER_GENERATION=40`
4. Deploy the backend and confirm the Render health check passes. Record the public API
   base URL, then append `/api/v1` when configuring the frontend.
5. In Vercel, import the same GitHub repository and set the project root directory to
   `web`. Set `NEXT_PUBLIC_API_URL` to the Render API base URL plus `/api/v1`, for
   example `https://your-studyforge-api.onrender.com/api/v1`. This URL is public; do
   not put a database URL, JWT secret, or Google key in any `NEXT_PUBLIC_` variable.
6. Deploy the frontend. If you change either hosted environment configuration, trigger
   a new deployment so the Next.js build receives `NEXT_PUBLIC_API_URL` and the API
   process receives its settings. Add the final production frontend origin to
   `API_CORS_ORIGINS` and redeploy the backend if that origin changes.
7. Test the deployed URL in order: register a new test account, log in, create a
   course, add text notes, upload a PDF/image under 20 MiB, generate questions, review
   and approve the question set, start practice and check feedback, start a timed exam,
   submit it, then confirm results and solutions appear as intended.

The existing upload path reads at most 20 MiB plus one byte into memory, extracts the
document content, and stores the extracted text in PostgreSQL. It does not persist the
original file to container-local storage, so container restarts do not lose an uploaded
file required by this workflow. File malware scanning, object storage, rate limiting,
login throttling, email verification, and background generation remain production
hardening gaps.

The initial Alembic migration creates the schema for a new database and has an
intentionally irreversible downgrade. It does not modify or reset an existing schema.
If a database already contains tables created by the old `create_all()` startup path,
back it up and review/adopt its current schema before enabling production migrations.
PostgreSQL migrations take a transaction-scoped advisory lock so multiple API instances
starting together do not race to apply the same revision. Do not run the initial
migration against an existing schema without a reviewed baseline; do not use
`alembic downgrade`.

## Production environment template

`.env.production.example` lists the required variables with placeholders only. Copy
values into the hosting dashboards rather than committing a populated environment
file. The API rejects production configuration with a missing/placeholder JWT secret
or database URL, non-PostgreSQL URL, missing Gemini key, or wildcard/non-HTTPS CORS
origins.
The frontend refuses API calls when `NEXT_PUBLIC_API_URL` is absent in production;
localhost is only its development fallback.

## Ongoing operations

- Use managed secrets and separate provider keys per environment.
- Use HTTPS, strict CORS, request limits, generation quotas and rate limits.
- Keep database backups and test restore procedures.
- Add metrics, redacted logs and error tracking.
- Add dependency/container scanning, rollout and rollback procedures.
- Verify Gemma/vision model availability, API behavior, quotas and pricing with the
  production key before inviting public users.
