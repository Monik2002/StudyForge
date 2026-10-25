from types import SimpleNamespace

from fastapi import HTTPException
import pytest
from sqlalchemy.exc import SQLAlchemyError
from studyforge import main
from studyforge.main import attemptdict, finalize


def test_health_check_returns_status_without_environment_details(monkeypatch):
    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            assert str(statement) == "SELECT 1"

    monkeypatch.setattr(main.engine, "connect", lambda: Connection())

    assert main.health() == {"status": "ok"}


def test_health_check_reports_database_unavailable_without_details(monkeypatch):
    def fail_to_connect():
        raise SQLAlchemyError("sensitive connection details")

    monkeypatch.setattr(main.engine, "connect", fail_to_connect)

    with pytest.raises(HTTPException) as error:
        main.health()

    assert error.value.status_code == 503
    assert error.value.detail == "Database unavailable"
    assert "sensitive" not in error.value.detail


def test_attemptdict_serializes_snapshot_without_revealing_answers():
    question_key = "question-1"
    attempt = SimpleNamespace(
        id="attempt-1",
        mode="exam",
        status="in_progress",
        started_at=None,
        expires_at=None,
        duration_seconds=1800,
        responses=[],
        question_snapshot=[{
            "key": question_key,
            "ordinal": 1,
            "qtype": "single_choice",
            "stem": "What does SSH provide?",
            "options": [
                {"id": "A", "text": "Secure remote access"},
                {"id": "B", "text": "Disk formatting"},
            ],
            "correct_option_ids": ["A"],
            "explanation": "SSH supports secure remote access.",
            "source_excerpt": "SSH provides encrypted access.",
            "topic_tags": ["networking"],
        }],
    )

    result = attemptdict(attempt)

    assert result["questions"] == [{
        "id": question_key,
        "key": question_key,
        "ordinal": 1,
        "qtype": "single_choice",
        "stem": "What does SSH provide?",
        "options": [
            {"id": "A", "text": "Secure remote access"},
            {"id": "B", "text": "Disk formatting"},
        ],
        "selected_option_ids": [],
        "is_flagged": False,
    }]


def test_scoring_exact_match():
    q={"key":"q1","correct_option_ids":["A"]}
    r=SimpleNamespace(question_key="q1",selected_option_ids=["A"],is_correct=None,awarded_points=None)
    a=SimpleNamespace(question_snapshot=[q],responses=[r],passing_score=70,score_points=None,max_points=None,percentage=None,passed=None,status="in_progress",submitted_at=None)
    finalize(None,a)
    assert a.percentage==100 and a.passed and r.is_correct
def test_multiple_select_requires_exact_match():
    q={"key":"q1","correct_option_ids":["A","B"]}
    r=SimpleNamespace(question_key="q1",selected_option_ids=["A"],is_correct=None,awarded_points=None)
    a=SimpleNamespace(question_snapshot=[q],responses=[r],passing_score=70,score_points=None,max_points=None,percentage=None,passed=None,status="in_progress",submitted_at=None)
    finalize(None,a)
    assert a.percentage==0 and not r.is_correct
