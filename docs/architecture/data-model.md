# Data model

- `User`: account email and password hash.
- `Course`: owned course.
- `Source`: pasted notes and SHA-256 fingerprint.
- `QuestionSet`: generated draft/approved bank and model/config metadata.
- `Question`: stem, options, answer IDs, explanation, difficulty, topic tags and source excerpt.
- `Attempt`: mode, state, immutable question snapshot, deadline and score.
- `AttemptResponse`: saved answer and review flag.

Ownership checks are performed by API queries. Historical attempts preserve question snapshots. Add reviewed migrations and explicit data deletion/retention policies before production.
