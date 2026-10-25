# StudyForge — Implementation Tasks

## Phase 0: Foundation and local environment
- [x] Create frontend, API, database and Docker Compose skeleton.
- [x] Add environment template and repository ignore rules.
- [x] Add initial architecture and operational documentation.
- [ ] Verify clean install from the ZIP on Windows and Linux.
- [ ] Add CI workflow for lint, type-check, tests, and builds.

## Phase 1: Accounts and course management
- [x] Register and login endpoints.
- [x] Bearer-token authentication and current-user endpoint.
- [x] Create/list courses.
- [x] Enforce basic resource ownership.
- [ ] Add email verification, password reset, revocation, login throttling, and session management.

## Phase 2: Notes and AI generation
- [x] Save pasted notes with size limit and SHA-256 hash.
- [x] Upload PDF, DOCX, TXT, Markdown, PNG, JPG, and WEBP notes (20 MB cap).
- [x] Use vision-capable extraction for PDF and image uploads; no extracted-content preview.
- [x] Integrate configurable Gemma API adapter.
- [x] Request structured question JSON.
- [x] Validate question type, option IDs, answer IDs, and explanations.
- [x] Save generated sets as drafts.
- [x] Add draft review and approval UI.
- [ ] Test configured model/key and quota end-to-end.
- [ ] Add prompt-injection and factual-grounding evaluation set.
- [ ] Add deduplication, retry policy, cost telemetry, quotas, and async jobs.
- [ ] Add malware scanning, private object storage, background extraction jobs, and richer PDF/DOCX extraction tests.

## Phase 3: Practice and exams
- [x] Start practice attempts.
- [x] Return immediate practice feedback.
- [x] Start timed exams with server-side expiration.
- [x] Save answers and review flags.
- [x] Snapshot question content per attempt.
- [x] Finalize attempts and calculate deterministic score.
- [x] Show result review and explanations.
- [ ] Add unanswered-question confirmation.
- [ ] Add race-condition/concurrent-submission tests.
- [ ] Add resume-after-refresh and network-retry UX.
- [ ] Verify answer-key secrecy with API integration tests.

## Phase 4: Quality and production readiness
- [ ] Add Alembic migrations and remove startup `create_all` in production.
- [ ] Add API integration tests against PostgreSQL.
- [ ] Add browser E2E tests for the complete user journey.
- [ ] Add lint, type checks, dependency and container scans.
- [ ] Add rate limits, security headers, strict production CORS, and HTTPS deployment.
- [ ] Add redacted logs, metrics, error tracking, and alerting.
- [ ] Add database backup/restore runbook and test restoration.
- [ ] Perform accessibility review and threat modeling.
- [ ] Document deployment, rollback, data retention, and deletion.
- [ ] Conduct human review of generated-question quality.

## Definition of done
A task is done when code is implemented, validation and error states are present, tests cover relevant behavior, documentation is updated, and no secrets are committed. Security-sensitive behavior must be enforced server-side.
