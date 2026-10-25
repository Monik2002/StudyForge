# StudyForge

StudyForge turns learner notes into reviewable question banks, practice sessions, timed exams, explanations, and results.

## Quick start
1. Copy `.env.example` to `.env`.
2. Set a strong `JWT_SECRET` and a server-side `GEMINI_API_KEY`. Question generation defaults to `GEMMA_MODEL_ID=gemma-4-26b-a4b-it`; PDF/image extraction uses the separate `DOCUMENT_VISION_MODEL_ID=gemini-2.5-flash`. Override either model ID only when your API key has access to it.
3. Run `docker compose up --build`.
4. Open `http://localhost:3000`; API docs: `http://localhost:8000/docs`.

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
This is a runnable MVP foundation, not a security-audited public production release. It does not yet include background generation jobs, malware scanning/private object storage, email verification/password reset, rate limiting, full observability, or a comprehensive end-to-end/security test suite. Question generation uses `GEMMA_MODEL_ID` (default `gemma-4-26b-a4b-it`); PDF/image uploads and embedded DOCX images use the separate `DOCUMENT_VISION_MODEL_ID` (default `gemini-2.5-flash`). Both require model access through the server-side `GEMINI_API_KEY`. Review AI-generated questions before approval. Verify model availability, capabilities, quotas and pricing in Google's current documentation.

## Documentation
See `docs/` for requirements, planning, architecture, repository structure, data model, API contract, AI pipeline, security, testing, operations, research and ADRs.
