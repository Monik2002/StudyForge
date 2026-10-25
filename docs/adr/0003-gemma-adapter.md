# ADR 0003: Isolate Gemma provider
Status: Accepted for MVP.

All provider calls go through `studyforge.ai`. Keep model ID configurable and store it on question sets so provider changes do not couple the whole app to SDK details.
