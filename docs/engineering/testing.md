# Testing strategy

Run: `cd api && pip install -e '.[dev]' && pytest`.

Included tests cover question schema validation and deterministic scoring. Before public production add PostgreSQL integration tests, resource-isolation tests, HTTP-level answer-key leakage tests, expiry/repeated/concurrent submission tests, browser E2E tests, accessibility checks, prompt-injection cases, upload parser tests, and a human-reviewed AI quality dataset.
