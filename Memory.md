# StudyForge — Project Memory and Decisions

This file is a project decision log, not a record of private user data. Update it when scope, architecture, or important implementation behavior changes.

## Product decisions
- Product name: StudyForge.
- Purpose: convert personal study notes into a question bank for practice and timed exams.
- Initial audience: students and self-directed technical learners.
- MVP question types: single choice, multiple select, true/false.
- Human review and approval is required before generated sets can be used.
- Practice mode provides immediate feedback; exam mode withholds answer keys until finalization.
- AI-generated content must be treated as fallible and reviewed.

## Technical decisions
- Frontend: Next.js App Router, React, TypeScript.
- Backend: FastAPI with Pydantic and SQLAlchemy.
- Database: PostgreSQL in Docker Compose.
- AI integration: server-side Gemma 4 (`gemma-4-26b-a4b-it`) for question generation through Google's Gemini API SDK; document extraction uses the separate Gemini model `gemini-2.5-flash`. Both model IDs are configurable through the environment.
- API key remains server-side; never place it in a `NEXT_PUBLIC_` variable.
- Use a modular monolith for the MVP.
- Backend owns authorization, exam deadlines, answer-key disclosure, scoring, and finalization.
- Assessment attempts snapshot questions so a later bank change does not alter an active attempt.
- Multiple-select grading currently requires an exact match.

## Repository conventions
- API code lives under `api/src/studyforge/`.
- Frontend code lives under `web/src/app/` and shared API types/helpers under `web/src/lib/`.
- Environment variable template: `.env.example`.
- Local orchestration: `compose.yaml`.
- Architecture decisions are recorded in `docs/adr/`.

## Known gaps / not yet verified
- End-to-end application startup has not been verified with the actual environment and provider key.
- A live Gemma 4 question-generation request using `google-genai` 1.75.0 and the configured API key succeeded on 2026-10-25; one returned question parsed and passed `validate_question`. This is a provider-path smoke test, not full application end-to-end verification. Availability, quotas, and pricing remain dependent on Google API access.
- Upload support now accepts PDF, DOCX, TXT, Markdown, PNG, JPG, and WEBP; PDF/image content is extracted through a vision-capable Gemini model, DOCX text/tables are extracted locally and embedded images are processed with vision (up to 12 images). No extracted-content preview is included.
- Background jobs, malware scanning/private object storage, email verification/password reset, rate limiting, production migrations, observability, and complete integration/E2E/security tests remain open.
- Treat current application as an MVP foundation, not production-hardened software.

## Update protocol
When a decision changes:
1. Update the relevant source documentation.
2. Record the decision and rationale here.
3. If the decision changes architecture, add or update an ADR under `docs/adr/`.
4. Keep completed and pending tasks aligned with `Tasks.md`.
