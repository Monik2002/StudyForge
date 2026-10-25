# Delivery plan

## Implemented in this MVP
- [x] Next.js UI and FastAPI API foundation
- [x] PostgreSQL models and Docker Compose
- [x] Register/login
- [x] Courses and pasted notes
- [x] Gemma generation adapter and structural validation
- [x] Draft question set and approval
- [x] Practice feedback
- [x] Exam snapshot, saved responses, server deadline and result scoring
- [x] Initial unit tests and documentation

## Before production
- [ ] PDF/DOCX ingestion and async job queue
- [ ] Complete Alembic migration workflow; remove startup create_all
- [ ] Authentication hardening, verification/reset/revocation and login throttling
- [ ] Rate limits, generation quotas and cost telemetry
- [ ] API integration, browser E2E, concurrency and security tests
- [ ] Secret/dependency/container scanning, monitoring and backups
- [ ] Accessibility review and threat model review
- [ ] Verify model ID, capabilities, quotas and pricing for the actual API key
