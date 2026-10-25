# StudyForge — Product Requirements Document

## 1. Product vision
StudyForge helps learners convert their own study notes into a reviewable question bank, then use that bank for deliberate practice or timed exam simulations.

## 2. Problem
Learners often have notes but lack a fast, consistent way to turn them into practice questions, test recall, and review mistakes. Generic question banks may not match the material being studied.

## 3. Target users
- Students preparing for academic exams.
- Technical learners preparing for certification exams.
- Self-directed learners studying from personal notes.

## 4. Goals
- Reduce the effort needed to create practice questions from notes.
- Keep questions grounded in learner-provided material.
- Separate practice with feedback from exam simulation.
- Save attempts and show transparent, deterministic results.
- Keep users in control of generated content through a review-and-approve step.

## 5. MVP scope
1. Register and sign in with email/password.
2. Create courses.
3. Upload PDF, DOCX, TXT, Markdown, or image notes; paste text remains available as an alternative.
4. Generate a question-set draft using a configured Gemma model.
5. Validate generated structure and let the learner review the draft.
6. Approve a question set before it can be used in an assessment.
7. Support single-choice, multiple-select, and true/false questions.
8. Practice mode with immediate feedback and explanations.
9. Timed exam mode with saved responses, navigation, review flags, and a server-owned deadline.
10. Submit, score, and review results.
11. Show basic course progress.

## 6. Non-goals for this MVP
- Collaborative courses or public question banks.
- PDF/DOCX ingestion and OCR.
- Spaced repetition and adaptive learning.
- Short-answer or essay grading.
- Payments, subscriptions, and mobile native apps.
- Production identity lifecycle such as email verification and password recovery.

## 7. Core user journey
Register → create course → upload a file or paste notes → generate draft → review questions and answer keys → approve → choose Practice or Exam → answer questions → submit → review score and explanations.

## 8. Functional acceptance criteria
- A user can only access their own courses, sources, question sets, and attempts.
- Notes have a configured size limit.
- AI output is parsed and structurally validated before persistence.
- Generated question sets remain drafts until explicitly approved.
- Assessment start is blocked unless the question set is approved.
- Active exam responses do not expose correct answers or explanations.
- The backend, not the browser, enforces exam expiration and scoring.
- Results are persisted and can be reopened after submission.
- Invalid API inputs return appropriate HTTP errors.

## 9. Quality attributes
- Responsive desktop and mobile web UI.
- Clear loading, empty, success, and error states.
- Secrets remain on the server.
- Deterministic grading.
- Testable service boundaries and documented deployment.
- Accessibility and security review required before public launch.

## 10. Success metrics to instrument
- Note-to-approved-question-set conversion rate.
- Question generation failure rate.
- Percentage of generated questions edited/rejected during review.
- Practice completion rate.
- Exam completion rate.
- Repeat attempts and score progression.
- API latency, model cost per generation, and provider error rate.

## 11. Known limitations
The current code is an MVP foundation. File uploads support PDF, DOCX, TXT, Markdown, PNG, JPG, and WEBP (20 MB limit). PDF and image extraction uses a configurable vision-capable Gemini model; DOCX text/tables are extracted locally and embedded images are sent for vision extraction (up to 12 per file); TXT/Markdown are extracted locally. Background jobs, comprehensive integration and browser tests, email verification/reset, rate limiting, migration tooling, observability, and production hardening remain incomplete. Model availability and structured-output behavior must be tested with the actual API key.
