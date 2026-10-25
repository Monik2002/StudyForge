import json
from types import SimpleNamespace

import pytest
from studyforge import ai
from studyforge.ai import AIProviderError, validate_question
from studyforge.config import Settings


def test_gemma_4_default_and_document_model_are_separate(monkeypatch):
    monkeypatch.delenv("GEMMA_MODEL_ID", raising=False)
    monkeypatch.delenv("DOCUMENT_VISION_MODEL_ID", raising=False)

    config = Settings(_env_file=None)

    assert config.gemma_model_id == "gemma-4-26b-a4b-it"
    assert config.document_vision_model_id == "gemini-2.5-flash"


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
    assert "GEMMA_MODEL_ID model access" in str(error.value)
    assert secret not in str(error.value)


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
