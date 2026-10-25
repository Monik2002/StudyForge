# Security

This MVP is for local development and evaluation, not an unrestricted public deployment.

- Keep `GEMINI_API_KEY` server-side; never expose it through `NEXT_PUBLIC_` variables.
- Replace the development JWT secret before use.
- Add HTTPS, managed secrets, rate limiting, abuse monitoring, security headers and CORS allowlists for hosted use.
- Add email verification, password reset, revocation and login throttling.
- Notes and model outputs are untrusted; validate output and never execute generated code.
- Enforce ownership on every resource. Exam answer keys remain hidden until finalization.
- Avoid logging source text, secrets or answer keys.
- Conduct OWASP ASVS-based review and test cross-user access.

References: https://ai.google.dev/gemini-api/docs/api-key · https://genai.owasp.org/llm-top-10/ · https://asvs.owasp.org/
