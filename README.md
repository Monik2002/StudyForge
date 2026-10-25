# StudyForge

StudyForge turns learner notes into reviewable question banks, practice sessions, timed exams, explanations, and results.

## Quick start
1. Copy `.env.example` to `.env`.
2. Set a strong `JWT_SECRET` and a server-side `GEMINI_API_KEY`. Question generation defaults to `GEMMA_MODEL_ID=gemma-4-26b-a4b-it`; PDF/image extraction uses the separate `DOCUMENT_VISION_MODEL_ID=gemini-2.5-flash`. Override either model ID only when your API key has access to it.
3. Run `docker compose up --build`.
4. Open `http://localhost:3000`; API docs: `http://localhost:8000/docs`.

## Production deployment

The supported deployment layout is a Next.js frontend on Vercel, the FastAPI Docker
service on Render, and a separately managed PostgreSQL database. The production
environment-variable template is `.env.production.example`; it contains placeholders
only and is not a credentials file. Set production values through the hosting dashboards.

Follow [the deployment and operations guide](docs/engineering/operations.md) for
service configuration, environment variables, database initialization, and smoke tests.
The API migrates a new production database before serving traffic. Existing databases
must be backed up and reviewed before adopting the migration baseline; never use the
initial migration's downgrade path.

## Project documents

The requested project-level specifications are at the repository root:
- `PRD.md` — product scope, goals, acceptance criteria and non-goals.
- `Architecture.md` — components, data flow and trust boundaries.
- `Rules.md` — AI grounding, validation, assessment integrity and privacy rules.
- `Design.md` — visual direction, responsive layout and interaction guidance.
- `Tasks.md` — implementation checklist and production-readiness work.
- `Memory.md` — decisions already made and known gaps.

Detailed engineering references remain in `docs/`.

## MVP features
- Email/password registration and login.
- Courses, pasted notes, and file uploads (PDF, DOCX, TXT, Markdown, PNG, JPG, WEBP; 20 MB maximum).
- Vision-assisted extraction for PDF/image notes, including diagram and screenshot interpretation; extracted-content preview is intentionally omitted.
- Gemma question generation, schema/domain validation, draft review and approval.
- Practice mode with immediate feedback.
- Timed exam mode, saved answers, question navigation, review flags, server-side deadline and post-submit results.
- Deterministic scoring and PostgreSQL persistence.

## Important limitations
This is a runnable MVP foundation, not a security-audited public production release. It does not yet include background generation jobs, malware scanning, email verification/password reset, rate limiting, full observability, or a comprehensive end-to-end/security test suite. Uploaded files are limited to 20 MiB, processed in memory, and not retained on the container filesystem; extracted note text is stored in PostgreSQL. Question generation uses `GEMMA_MODEL_ID` (default `gemma-4-26b-a4b-it`); PDF/image uploads and embedded DOCX images use the separate `DOCUMENT_VISION_MODEL_ID` (default `gemini-2.5-flash`). Both require model access through the server-side `GEMINI_API_KEY`. Review AI-generated questions before approval. Verify model availability, capabilities, quotas and pricing in Google's current documentation.

## Documentation
See `docs/` for requirements, planning, architecture, repository structure, data model, API contract, AI pipeline, security, testing, operations, research and ADRs.
