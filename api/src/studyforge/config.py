from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    database_url: str = "sqlite:///./studyforge-dev.db"
    jwt_secret: str = "unsafe-development-secret-change-me"
    jwt_expire_minutes: int = 720
    gemini_api_key: str | None = None
    gemma_model_id: str = "gemma-4-26b-a4b-it"
    document_vision_model_id: str = "gemini-2.5-flash"
    api_cors_origins: str = "http://localhost:3000"
    max_source_chars: int = 100000
    max_questions_per_generation: int = 40
    @property
    def cors_origins(self):
        return [x.strip() for x in self.api_cors_origins.split(",") if x.strip()]
settings = Settings()
