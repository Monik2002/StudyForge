import json
from types import SimpleNamespace

import pytest
from studyforge import ai
from studyforge.ai import AIProviderError, validate_question
from studyforge.config import Settings
from studyforge.db import normalize_database_url


def test_gemma_4_default_and_document_model_are_separate(monkeypatch):
    monkeypatch.delenv("GEMMA_MODEL_ID", raising=False)
    monkeypatch.delenv("DOCUMENT_VISION_MODEL_ID", raising=False)

    config = Settings(_env_file=None)

    assert config.gemma_model_id == "gemma-4-26b-a4b-it"
    assert config.document_vision_model_id == "gemini-2.5-flash"


def test_production_settings_reject_development_defaults():
    with pytest.raises(ValueError, match="Invalid production configuration"):
        Settings(_env_file=None, app_env="production")


def test_production_configuration_errors_do_not_include_credentials():
    database_password = "database-password-sentinel"
    jwt_secret = "jwt-secret-sentinel"
    gemini_api_key = "gemini-key-sentinel"

    with pytest.raises(ValueError) as error:
        Settings(
            _env_file=None,
            app_env="production",
            database_url=f"postgresql://user:{database_password}@db.example.test/studyforge",
            jwt_secret=jwt_secret,
            gemini_api_key=gemini_api_key,
            api_cors_origins="*",
        )

    assert database_password not in str(error.value)
    assert jwt_secret not in str(error.value)
    assert gemini_api_key not in str(error.value)


def test_production_settings_accept_explicit_origins_and_secrets():
    config = Settings(
        _env_file=None,
        app_env="production",
        database_url="postgresql://studyforge:encoded%40password@db.example.test/studyforge",
        jwt_secret="random-production-secret-with-more-than-32-characters",
        gemini_api_key="google-api-key",
        api_cors_origins="https://studyforge.vercel.app",
    )

    assert config.cors_origins == ["https://studyforge.vercel.app"]


def test_production_settings_reject_database_url_placeholders():
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Settings(
            _env_file=None,
            app_env="production",
            database_url="postgresql://<user>:<password>@<host>:5432/<database>",
            jwt_secret="random-production-secret-with-more-than-32-characters",
            gemini_api_key="google-api-key",
            api_cors_origins="https://studyforge.vercel.app",
        )


def test_production_settings_reject_wildcard_or_non_origin_cors_values():
    with pytest.raises(ValueError, match="API_CORS_ORIGINS"):
        Settings(
            _env_file=None,
            app_env="production",
            database_url="postgresql://user:password@db.example.test/studyforge",
            jwt_secret="random-production-secret-with-more-than-32-characters",
            gemini_api_key="google-api-key",
            api_cors_origins="*",
        )

    with pytest.raises(ValueError, match="API_CORS_ORIGINS"):
        Settings(
            _env_file=None,
            app_env="production",
            database_url="postgresql://user:password@db.example.test/studyforge",
            jwt_secret="random-production-secret-with-more-than-32-characters",
            gemini_api_key="google-api-key",
            api_cors_origins="https://studyforge.vercel.app/api",
        )

    with pytest.raises(ValueError, match="API_CORS_ORIGINS"):
        Settings(
            _env_file=None,
            app_env="production",
            database_url="postgresql://user:password@db.example.test/studyforge",
            jwt_secret="random-production-secret-with-more-than-32-characters",
            gemini_api_key="google-api-key",
            api_cors_origins="https://studyforge.vercel.app/",
        )

    with pytest.raises(ValueError, match="API_CORS_ORIGINS"):
        Settings(
            _env_file=None,
            app_env="production",
            database_url="postgresql://user:password@db.example.test/studyforge",
            jwt_secret="random-production-secret-with-more-than-32-characters",
            gemini_api_key="google-api-key",
            api_cors_origins="https://*.vercel.app",
        )


def test_database_url_uses_psycopg_and_decodes_encoded_credentials():
    url = normalize_database_url(
        "postgresql://studyforge:p%40ss%3Aword@db.example.test:5432/studyforge"
    )

    assert url.drivername == "postgresql+psycopg"
    assert url.password == "p@ss:word"


def test_generate_questions_uses_configured_model_and_parses_json(monkeypatch):
    question = {
        "type": "single_choice",
        "stem": "What does SSH provide?",
        "options": [
            {"id": "A", "text": "Secure remote access"},
            {"id": "B", "text": "Disk formatting"},
        ],
        "correct_option_ids": ["A"],
        "explanation": "SSH supports secure remote access.",
    }
    request = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            request.update(kwargs)
            return SimpleNamespace(text=json.dumps({"questions": [question]}))

    monkeypatch.setattr(ai.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(ai.settings, "gemma_model_id", "gemma-4-26b-a4b-it")
    monkeypatch.setattr(ai.genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))

    questions, model_id = ai.generate_questions(
        "SSH provides secure remote access to systems.", "Networking", 1, ["single_choice"], "easy"
    )

    assert model_id == "gemma-4-26b-a4b-it"
    assert questions == [question]
    assert request["model"] == "gemma-4-26b-a4b-it"
    assert request["config"].response_mime_type == "application/json"


def test_generate_questions_reports_provider_failure_without_credentials(monkeypatch):
    secret = "do-not-leak-this-key"

    class FakeModels:
        def generate_content(self, **kwargs):
            raise RuntimeError(f"request failed with {secret}")

    monkeypatch.setattr(ai.settings, "gemini_api_key", secret)
    monkeypatch.setattr(ai.genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))

    with pytest.raises(AIProviderError) as error:
        ai.generate_questions("Study notes with enough content.", "Course", 1, ["single_choice"], "easy")

    assert "RuntimeError" in str(error.value)
    assert "GEMMA_MODEL_ID" in str(error.value)
    assert secret not in str(error.value)


def test_extract_document_uses_explicit_multimodal_content(monkeypatch):
    request = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            request.update(kwargs)
            return SimpleNamespace(text="Extracted notes with enough readable content.")

    monkeypatch.setattr(ai.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(ai.settings, "document_vision_model_id", "gemini-2.5-flash")
    monkeypatch.setattr(ai.genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))

    text = ai.extract_document_content("notes.pdf", b"%PDF test", "application/pdf")

    content = request["contents"][0]
    assert text == "Extracted notes with enough readable content."
    assert request["model"] == "gemini-2.5-flash"
    assert isinstance(content, ai.types.Content)
    assert content.role == "user"
    assert len(content.parts) == 2
    assert content.parts[0].text.startswith("Extract comprehensive study notes")
    assert content.parts[1].inline_data.mime_type == "application/pdf"


def test_extract_document_404_names_model_and_setting_without_leaking_error(monkeypatch):
    secret = "do-not-leak-this-key"

    class ProviderNotFound(Exception):
        code = 404

    class FakeModels:
        def generate_content(self, **kwargs):
            raise ProviderNotFound(f"404 for {secret}")

    monkeypatch.setattr(ai.settings, "gemini_api_key", secret)
    monkeypatch.setattr(ai.settings, "document_vision_model_id", "invalid-test-model")
    monkeypatch.setattr(ai.genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))

    with pytest.raises(AIProviderError) as error:
        ai.extract_document_content("notes.pdf", b"%PDF test", "application/pdf")

    message = str(error.value)
    assert "provider status 404" in message
    assert "DOCUMENT_VISION_MODEL_ID" in message
    assert "invalid-test-model" in message
    assert "available to this API project" in message
    assert secret not in message
    assert "404 for" not in message


def test_generate_questions_rejects_malformed_json(monkeypatch):
    class FakeModels:
        def generate_content(self, **kwargs):
            return SimpleNamespace(text="not JSON")

    monkeypatch.setattr(ai.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(ai.genai, "Client", lambda **kwargs: SimpleNamespace(models=FakeModels()))

    with pytest.raises(AIProviderError, match="Question generation failed"):
        ai.generate_questions("Study notes with enough content.", "Course", 1, ["single_choice"], "easy")


def test_valid_question():
    q=validate_question({"type":"single_choice","stem":"What does SSH provide?","options":[{"id":"A","text":"Secure remote access"},{"id":"B","text":"Disk formatting"}],"correct_option_ids":["A"],"explanation":"SSH supports secure remote access.","difficulty":"easy"},1)
    assert q["correct_option_ids"]==["A"]
def test_invalid_answer_id_rejected():
    with pytest.raises(ValueError):
        validate_question({"type":"single_choice","stem":"What does SSH provide?","options":[{"id":"A","text":"Remote access"},{"id":"B","text":"Formatting"}],"correct_option_ids":["Z"],"explanation":"This is a useful explanation."},1)
