"""Regression tests for API paths affected by SQLite contention and CORS."""
from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.main import app
from database import database as database_module
from app.matchmaking.routes import init_matchmaking_tables


@pytest.fixture
def client(tmp_path, monkeypatch):
    main_db = tmp_path / "mathweb_test.db"
    ai_db = tmp_path / "mathweb_ai_history_test.sqlite3"
    monkeypatch.setenv("MATHWEB_DB_PATH", str(main_db))
    monkeypatch.setenv("MATHWEB_AI_HISTORY_DB_PATH", str(ai_db))
    monkeypatch.setattr(database_module, "DATABASE_PATH", main_db)
    database_module.init_database()
    init_matchmaking_tables()
    with TestClient(app) as test_client:
        yield test_client


def register(client: TestClient, username: str):
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "safePass123"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data["user"], {"Authorization": f"Bearer {data['token']}"}


def test_cors_preflight_for_local_frontend(client: TestClient):
    origin = "http://127.0.0.1:5500"
    response = client.options(
        "/api/matchmaking/random/join",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin


def test_random_matchmaking_does_not_lock_when_ai_generates_questions(client: TestClient):
    _, headers_a = register(client, "QueuePlayerA")
    _, headers_b = register(client, "QueuePlayerB")
    settings = {
        "grade": 10,
        "topics": ["menh_de_tap_hop"],
        "difficulty": "easy",
        "question_type": "multiple_choice",
    }

    first = client.post("/api/matchmaking/random/join", headers=headers_a, json=settings)
    assert first.status_code == 200, first.text
    assert first.json()["status"] == "QUEUED"

    second = client.post("/api/matchmaking/random/join", headers=headers_b, json=settings)
    assert second.status_code == 200, second.text
    assert second.json()["status"] == "MATCHED"
    assert second.json()["question_count"] == 10

    match_id = second.json()["match_id"]
    match_details = client.get(f"/api/matchmaking/match/{match_id}", headers=headers_a)
    assert match_details.status_code == 200, match_details.text

    started = client.post(f"/api/matchmaking/match/{match_id}/start", headers=headers_a)
    assert started.status_code == 200, started.text
    assert started.json()["status"] == "PLAYING"

    answer = client.post(
        f"/api/matchmaking/match/{match_id}/answer",
        headers=headers_a,
        json={"question_index": 0, "answer": "__intentional_test_answer__"},
    )
    assert answer.status_code == 200, answer.text
    assert answer.json()["correct"] is False
    assert answer.json()["correct_answer"] is not None

    progress = client.get(f"/api/matchmaking/match/{match_id}/progress", headers=headers_b)
    assert progress.status_code == 200, progress.text
    assert progress.json()["you"]["current"] == 0
    assert progress.json()["opponent"]["current"] == 1


def test_friend_request_and_chat_message_flow(client: TestClient):
    user_a, headers_a = register(client, "ChatPlayerA")
    user_b, headers_b = register(client, "ChatPlayerB")

    sent = client.post(
        "/api/friends/request",
        headers=headers_a,
        json={"player_id": user_b["player_id"]},
    )
    assert sent.status_code == 200, sent.text

    incoming = client.get("/api/friends/requests", headers=headers_b)
    assert incoming.status_code == 200, incoming.text
    request_id = incoming.json()[0]["id"]

    accepted = client.post(f"/api/friends/accept/{request_id}", headers=headers_b)
    assert accepted.status_code == 200, accepted.text

    message = "Tin nhắn kiểm thử tích hợp"
    sent_message = client.post(
        f"/api/chat/{user_b['id']}/messages",
        headers=headers_a,
        json={"content": message},
    )
    assert sent_message.status_code == 200, sent_message.text

    history = client.get(f"/api/chat/{user_a['id']}/messages", headers=headers_b)
    assert history.status_code == 200, history.text
    assert any(item["content"] == message for item in history.json())
