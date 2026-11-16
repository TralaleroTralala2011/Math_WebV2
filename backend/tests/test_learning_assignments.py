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
    monkeypatch.setattr(admin_routes, "BOOTSTRAP_PASSWORD", "TestOnlyAdminPass2026")
    admin_routes.ensure_admin_schema_and_account()
    with TestClient(app) as client:
        yield client


def test_assignment_flow_and_personalized_path(learning_client, monkeypatch):
    client = learning_client
    registered = client.post("/api/auth/register", json={"username": "LearningStudent", "password": "safePass123"})
    assert registered.status_code == 200, registered.text
    learner = registered.json()["user"]
    learner_headers = {"Authorization": f"Bearer {registered.json()['token']}"}
    admin_login = client.post("/api/auth/login", json={"username": "admin19022011", "password": "TestOnlyAdminPass2026"})
    assert admin_login.status_code == 200, admin_login.text
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['token']}"}
    # AI TAP HOC no longer falls back to unrelated synthetic questions.
    monkeypatch.setattr(ai_service, "generate_set", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("AI fallback forbidden")))
    created = client.post("/api/admin/learning/assignments", headers=admin_headers, json={"title": "Ôn hệ bất phương trình", "description": "Làm cẩn thận", "grade": 10, "topic": "he_bat_phuong_trinh", "difficulty": "medium", "question_type": "short_answer", "question_count": 1, "student_ids": [learner["id"]]})
    assert created.status_code == 200, created.text
    assignment_id = created.json()["id"]
    mine = client.get("/api/admin/learning/assignments/mine", headers=learner_headers)
    assert mine.status_code == 200 and mine.json()["assignments"][0]["id"] == assignment_id
    started = client.post(f"/api/admin/learning/assignments/{assignment_id}/start", headers=learner_headers, json={})
    assert started.status_code == 200, started.text
    assert "answer" not in started.json()["questions"][0]
    with database_module.get_connection() as con:
        record=con.execute("SELECT questions_json FROM learning_assignment_targets WHERE assignment_id=?",(assignment_id,)).fetchone()
        original=__import__('json').loads(record['questions_json'])[0]
    assert original['source']=='150_CHU_DE_WORD' and original['source_word'].endswith('.docx')
    assert started.json()['questions'][0]['question']==original['question']
    submitted = client.post(f"/api/admin/learning/assignments/{assignment_id}/submit", headers=learner_headers, json={"answers": {"0": original['answer']}, "elapsed_seconds": 12})
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["score"] == 100.0
    assert client.get("/api/admin/learning/path", headers=learner_headers).status_code == 200
    results = client.get(f"/api/admin/learning/assignments/{assignment_id}/results", headers=admin_headers)
    assert results.status_code == 200 and results.json()["results"][0]["status"] == "submitted"
