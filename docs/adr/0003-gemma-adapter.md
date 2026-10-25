# ADR 0003: Isolate Gemma provider
Status: Accepted for MVP.

All provider calls go through `studyforge.ai`. Keep model IDs configurable and store the question-generation model ID on question sets so provider changes do not couple the whole app to SDK details. The default question-generation model is `gemma-4-26b-a4b-it`, called through the Google Gemini API; document extraction remains on the separate `gemini-2.5-flash` default.
