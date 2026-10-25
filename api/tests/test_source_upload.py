import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from studyforge.config import settings
from studyforge.db import Base, get_db
from studyforge.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()


def create_course(client):
    auth = client.post(
        "/api/v1/auth/register",
        json={"email": "source-preview@example.com", "password": "Synthetic-QA-Password-123"},
    )
    assert auth.status_code == 201
    headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}
    course = client.post(
        "/api/v1/courses",
        json={"title": "Upload preview test", "description": "Synthetic test fixture."},
        headers=headers,
    )
    assert course.status_code == 201
    return course.json()["id"], headers


def test_text_upload_returns_extracted_content_for_review(client):
    course_id, headers = create_course(client)
    extracted_text = (
        "DNS translates domain names into IP addresses. An A record maps a name to IPv4, "
        "while an AAAA record maps a name to IPv6. This synthetic note is used to test "
        "that the owner can review extracted text before starting question generation."
    )

    response = client.post(
        f"/api/v1/courses/{course_id}/sources/upload",
        headers=headers,
        files={"file": ("networking.txt", io.BytesIO(extracted_text.encode()), "text/plain")},
    )

    assert response.status_code == 201
    assert response.json()["content"] == extracted_text
    assert response.json()["extraction"] == "text"


def test_vision_upload_returns_extracted_content_and_model_type(client, monkeypatch):
    course_id, headers = create_course(client)
    extracted_text = (
        "The diagram shows a client querying a recursive DNS resolver, which then looks "
        "up the authoritative nameserver before returning the resolved IP address."
    )
    monkeypatch.setattr("studyforge.main.extract_document_content", lambda *args: extracted_text)

    response = client.post(
        f"/api/v1/courses/{course_id}/sources/upload",
        headers=headers,
        files={"file": ("dns-diagram.png", io.BytesIO(b"synthetic image bytes"), "image/png")},
    )

    assert response.status_code == 201
    assert response.json()["content"] == extracted_text
    assert response.json()["extraction"] == "vision"
