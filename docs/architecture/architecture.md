# Architecture

Next.js App Router/React/TypeScript frontend; FastAPI/Pydantic API; SQLAlchemy/PostgreSQL; Gemma via Google's Gemini API. The app is a modular monolith, not microservices.

The frontend owns presentation only. Backend owns authentication, resource authorization, attempt state, timers, scoring, and answer-key disclosure. The AI adapter is isolated in `api/src/studyforge/ai.py`. Active attempts use snapshots so later question-bank edits cannot silently change an exam.

Production evolution: queue for generation, private object storage, robust identity lifecycle, rate limits, telemetry, managed secrets, migration gates, and backup/restore verification.
