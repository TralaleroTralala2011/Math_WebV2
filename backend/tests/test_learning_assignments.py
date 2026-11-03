from fastapi.testclient import TestClient
import pytest

from app.main import app
from app import admin_routes
from app.ai.routes import service as ai_service
from database import database as database_module
from app.matchmaking.routes import init_matchmaking_tables


@pytest.fixture
def learning_client(tmp_path, monkeypatch):
    db = tmp_path / "learning_assignments.db"
    monkeypatch.setenv("MATHWEB_DB_PATH", str(db))
    monkeypatch.setenv("MATHWEB_AI_HISTORY_DB_PATH", str(tmp_path / "ai_history.db"))
    monkeypatch.setattr(database_module, "DATABASE_PATH", db)
    database_module.init_database()
    init_matchmaking_tables()
    admin_routes.ensure_admin_schema_and_account()
    with TestClient(app) as client:
        yield client


def test_assignment_flow_and_personalized_path(learning_client, monkeypatch):
    client = learning_client
    registered = client.post("/api/auth/register", json={"username": "LearningStudent", "password": "safePass123"})
    assert registered.status_code == 200, registered.text
    learner = registered.json()["user"]
    learner_headers = {"Authorization": f"Bearer {registered.json()['token']}"}
    admin_login = client.post("/api/auth/login", json={"username": "admin19022011", "password": "adminsitinh"})
    assert admin_login.status_code == 200, admin_login.text
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['token']}"}
    monkeypatch.setattr(ai_service, "generate_set", lambda *args, **kwargs: {"questions": [{"question": "Tính 2 + 2", "options": ["A. 3", "B. 4", "C. 5", "D. 6"], "answer": "B", "solution": "2 + 2 = 4", "question_type": "multiple_choice"}]})
    created = client.post("/api/admin/learning/assignments", headers=admin_headers, json={"title": "Ôn tập phép tính", "description": "Làm cẩn thận", "grade": 10, "topic": "menh_de_tap_hop", "difficulty": "easy", "question_type": "multiple_choice", "question_count": 1, "student_ids": [learner["id"]]})
    assert created.status_code == 200, created.text
    assignment_id = created.json()["id"]
    mine = client.get("/api/admin/learning/assignments/mine", headers=learner_headers)
    assert mine.status_code == 200 and mine.json()["assignments"][0]["id"] == assignment_id
    started = client.post(f"/api/admin/learning/assignments/{assignment_id}/start", headers=learner_headers, json={})
    assert started.status_code == 200, started.text
    assert "answer" not in started.json()["questions"][0]
    archived = client.get("/api/admin/questions?limit=20", headers=admin_headers)
    assert archived.status_code == 200, archived.text
    assert any(q["question"] == "Tính 2 + 2" for q in archived.json()["questions"])
    submitted = client.post(f"/api/admin/learning/assignments/{assignment_id}/submit", headers=learner_headers, json={"answers": {"0": "B. 4"}, "elapsed_seconds": 12})
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["score"] == 100.0
    assert client.get("/api/admin/learning/path", headers=learner_headers).status_code == 200
    results = client.get(f"/api/admin/learning/assignments/{assignment_id}/results", headers=admin_headers)
    assert results.status_code == 200 and results.json()["results"][0]["status"] == "submitted"
