# API contract

Base prefix: `/api/v1`. Interactive OpenAPI documentation is at `/docs`.

- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `GET /courses`, `POST /courses`
- `POST /courses/{course_id}/sources/text`
- `POST /sources/{source_id}/question-sets`
- `GET /courses/{course_id}/question-sets`, `GET /question-sets/{set_id}`
- `POST /question-sets/{set_id}/approve`
- `POST /question-sets/{set_id}/practice-attempts`
- `POST /question-sets/{set_id}/exam-attempts`
- `GET /attempts/{attempt_id}`
- `PUT /attempts/{attempt_id}/responses/{question_key}`
- `POST /attempts/{attempt_id}/responses/{question_key}/check` (practice only)
- `POST /attempts/{attempt_id}/submit`
- `GET /attempts/{attempt_id}/results`
- `GET /courses/{course_id}/progress`

Exam DTOs omit correct answers/explanations while an attempt is active; finalized results reveal them.
