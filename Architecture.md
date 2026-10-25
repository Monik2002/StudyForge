# StudyForge — Architecture

## 1. Overview
StudyForge is a modular monolith with a Next.js frontend, FastAPI backend, PostgreSQL persistence, and a server-side Gemma provider adapter.

```text
Browser
  │ HTTPS in production
  ▼
Next.js / React / TypeScript
  │ Bearer token + JSON API
  ▼
FastAPI ─────── Gemma question generation API
   └─────────── Gemini vision/document extraction API
  │                 ▲
  │                 │ server-side API key
  ▼
PostgreSQL
```

## 2. Components
- **Web:** `web/src/app/` contains the dashboard, course and question-set workflow, and assessment UI. `web/src/lib/api.ts` centralizes API requests and types.
- **API:** `api/src/studyforge/main.py` exposes HTTP endpoints and enforces authentication, ownership, assessment state, and grading.
- **AI adapter:** `api/src/studyforge/ai.py` constructs the prompt, calls the configured model, parses JSON, and validates generated questions.
- **Persistence:** `models.py` defines users, courses, sources, question sets, questions, attempts, and responses. `db.py` creates SQLAlchemy sessions.
- **Configuration:** `config.py` reads environment variables; `.env.example` documents local configuration.
- **Deployment:** `compose.yaml` runs the database, API, and web service.

## 3. Data flow
1. User creates a course and submits notes.
2. API validates ownership and source size, then stores the source and content hash.
3. TXT/Markdown and DOCX text/tables are extracted locally; PDF/image uploads and embedded DOCX images are sent to the configured vision-capable model to interpret text, tables, diagrams, and screenshots (DOCX image processing is capped at 12 images).
4. API sends the resulting source notes to the configured Gemma model for question generation.
4. Provider output is parsed and validated; valid questions are stored as a draft.
5. User reviews and approves the draft.
6. API snapshots approved questions when an attempt starts.
7. The browser saves responses through authenticated endpoints.
8. API enforces exam deadline, calculates score, finalizes the attempt, and reveals the answer review.

## 4. Trust boundaries
- The browser is untrusted; client-side state is never authoritative for authorization or grading.
- User notes and model output are untrusted content.
- API keys and JWT signing secrets are server-side only.
- Resource ownership is checked by the backend.
- Active assessment responses omit answer keys and explanations.

## 5. Architecture decisions
- Use a modular monolith for a small MVP to reduce operational complexity.
- Keep provider integration behind one adapter so model changes are localized.
- Snapshot questions at attempt start so later edits do not change an existing attempt.
- Keep scoring deterministic and server-owned.
- Use PostgreSQL in Docker Compose; SQLite is intended only for local smoke testing.

## 6. Production evolution
Before a public launch, add reviewed Alembic migrations, a background job queue, file parsing and private object storage, stronger authentication lifecycle, rate limiting and quotas, structured logs and metrics, managed secrets, backups/restore drills, and automated security/integration/E2E tests.
