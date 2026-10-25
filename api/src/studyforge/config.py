from urllib.parse import urlsplit

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def is_explicit_https_origin(origin: str) -> bool:
    parsed = urlsplit(origin)
    return (
        "*" not in origin
        and parsed.scheme == "https"
        and bool(parsed.hostname)
        and not parsed.path
        and not parsed.query
        and not parsed.fragment
        and not parsed.username
        and not parsed.password
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = Field(default="sqlite:///./studyforge-dev.db", repr=False)
    jwt_secret: str = Field(default="unsafe-development-secret-change-me", repr=False)
    jwt_expire_minutes: int = 720
    gemini_api_key: str | None = Field(default=None, repr=False)
    gemma_model_id: str = "gemma-4-26b-a4b-it"
    document_vision_model_id: str = "gemini-2.5-flash"
    api_cors_origins: str = Field(default="http://localhost:3000", repr=False)
    max_source_chars: int = 100000
    max_questions_per_generation: int = 40

    @property
    def cors_origins(self):
        return [x.strip() for x in self.api_cors_origins.split(",") if x.strip()]

    def model_post_init(self, __context):
        if self.app_env.lower() != "production":
            return

        problems = []
        if len(self.jwt_secret) < 32 or self.jwt_secret.startswith(("unsafe-", "replace-", "GENERATE_")):
            problems.append("JWT_SECRET must be a strong, non-placeholder value of at least 32 characters")
        if (
            not self.database_url.startswith(("postgres://", "postgresql://", "postgresql+psycopg://"))
            or any(f"<{placeholder}>" in self.database_url for placeholder in ("user", "password", "host", "database"))
        ):
            problems.append("DATABASE_URL must be a configured PostgreSQL connection URL")
        if not self.gemini_api_key or self.gemini_api_key.startswith(("replace-", "YOUR_")):
            problems.append("GEMINI_API_KEY must be set to a server-side Google API key")

        origins = self.cors_origins
        if not origins or "*" in origins:
            problems.append("API_CORS_ORIGINS must contain explicit HTTPS frontend origins")
        elif any(not is_explicit_https_origin(origin) for origin in origins):
            problems.append("API_CORS_ORIGINS must contain explicit HTTPS frontend origins")

        if problems:
            raise ValueError("Invalid production configuration: " + "; ".join(problems))


settings = Settings()
