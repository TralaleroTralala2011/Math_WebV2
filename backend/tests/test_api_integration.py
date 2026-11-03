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
    current_for_first = client.get("/api/matchmaking/current", headers=headers_a)
    assert current_for_first.status_code == 200, current_for_first.text
    assert current_for_first.json()["match_id"] == match_id
    assert current_for_first.json()["status"] in {"STARTING", "PLAYING"}
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


def test_direct_battle_invite_accept_and_start(client: TestClient):
    user_a, headers_a = register(client, "BattleInviteA")
    user_b, headers_b = register(client, "BattleInviteB")

    # Omitting optional topic settings must still use valid grade defaults.
    invite = client.post(
        "/api/matchmaking/invite",
        headers=headers_a,
        json={"player_id": user_b["player_id"]},
    )
    assert invite.status_code == 200, invite.text
    invite_data = invite.json()
    assert invite_data["status"] == "INVITED"
    assert invite_data["question_count"] == 10

    pending = client.get("/api/matchmaking/invites", headers=headers_b)
    assert pending.status_code == 200, pending.text
    assert any(int(item.get("match_id", -1)) == invite_data["match_id"] for item in pending.json().get("invites", []))

    match_id = invite_data["match_id"]
    accepted = client.post(f"/api/matchmaking/match/{match_id}/accept", headers=headers_b)
    assert accepted.status_code == 200, accepted.text

    started = client.post(f"/api/matchmaking/match/{match_id}/start", headers=headers_a)
    assert started.status_code == 200, started.text
    assert started.json()["status"] in {"STARTING", "PLAYING"}


def test_battle_page_includes_presence_heartbeat():
    from pathlib import Path

    battle_page = Path(__file__).resolve().parents[2] / "battle.html"
    html = battle_page.read_text(encoding="utf-8")
    assert 'src="js/presence.js"' in html
    assert html.index('src="js/api-config.js"') < html.index('src="js/presence.js"') < html.index('src="js/battle.js"')


def test_trial_button_routes_to_dedicated_trial_practice_page():
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    demo_js = (project_root / "js" / "demo-mode.js").read_text(encoding="utf-8")
    trial_page = project_root / "trial-practise.html"
    auth_js = (project_root / "js" / "practise-auth.js").read_text(encoding="utf-8")

    assert "trial-practise.html?trial=1" in demo_js
    assert trial_page.is_file()
    assert 'params.get("trial") !== "1"' in trial_page.read_text(encoding="utf-8")
    assert 'currentPage !== "trial-practise.html"' in auth_js


def test_friend_search_accepts_player_id_case_insensitively(client: TestClient):
    user_a, headers_a = register(client, "FriendSearchCaseA")
    user_b, _ = register(client, "FriendSearchCaseB")
    player_id = str(user_b["player_id"])
    response = client.get(
        "/api/friends/search",
        params={"player_id": player_id.swapcase()},
        headers=headers_a,
    )
    assert response.status_code == 200, response.text
    assert int(response.json()["id"]) == int(user_b["id"])


def test_admin_hierarchy_and_question_file_import(client: TestClient):
    from app.auth.routes import create_admin_token
    from app.admin_routes import ensure_admin_schema_and_account
    ensure_admin_schema_and_account()

    conn = database_module.get_connection()
    try:
        admin = conn.execute("SELECT id, username, auth_version FROM admin_accounts WHERE status='active' LIMIT 1").fetchone()
        assert admin is not None
        token = create_admin_token(admin["id"], admin["username"], admin["auth_version"])
    finally:
        conn.close()
    headers = {"Authorization": f"Bearer {token}"}
    hierarchy = client.get("/api/admin/library/hierarchy", headers=headers)
    assert hierarchy.status_code == 200, hierarchy.text
    data = hierarchy.json()
    assert data["total_topics"] >= 150
    assert data["total_games"] >= 474
    topic = next(t for t in data["topics"] if t["id"] == "g10_advanced_inequalities")
    assert topic["games"]
    game = topic["games"][0]
    upload = client.post("/api/admin/questions/import-file", headers=headers, json={
        "filename": "questions.json",
        "grade": 10,
        "default_topic": topic["id"],
        "default_game_id": game["game_id"],
        "content": __import__("json").dumps({"questions": [{
            "question": "Tính 2 + 3 trong bài kiểm tra nhập tệp?",
            "correct_answer": "5",
            "choices": ["4", "5", "6", "7"],
            "topic": topic["id"],
            "game": game["game_id"],
            "difficulty": "nền tảng",
            "explanation": "Cộng hai số tự nhiên: 2 + 3 = 5."
        }]}, ensure_ascii=False),
    })
    assert upload.status_code == 200, upload.text
    assert upload.json()["added"] == 1
    saved = client.get("/api/admin/questions", headers=headers, params={"grade": 10, "topic": topic["id"], "game_id": game["game_id"]})
    assert saved.status_code == 200, saved.text
    assert any(q["question"].startswith("Tính 2 + 3") for q in saved.json()["questions"])


def test_learning_coach_saves_user_selected_difficulty(client: TestClient):
    _, headers = register(client, "LearningCoachUser")
    initial = client.get("/api/users/me/learning-coach", headers=headers)
    assert initial.status_code == 200, initial.text
    assert initial.json()["suggested_difficulty"] in {"easy", "medium", "hard"}
    saved = client.put("/api/users/me/difficulty", headers=headers, json={"difficulty": "hard"})
    assert saved.status_code == 200, saved.text
    refreshed = client.get("/api/users/me/learning-coach", headers=headers)
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["difficulty"] == "hard"
    assert refreshed.json()["suggested_difficulty"] == "hard"
