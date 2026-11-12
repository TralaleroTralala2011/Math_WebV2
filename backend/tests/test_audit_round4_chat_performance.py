"""Round 4 regression coverage for chat history, unread summary and warm DB access."""
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import study_suite_routes as study
from app import final_features_routes as final
from database import database as db
from app.matchmaking.routes import init_matchmaking_tables


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DATABASE_PATH', tmp_path / 'chat_perf.sqlite3')
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'ai_perf.sqlite3'))
    db.init_database()
    init_matchmaking_tables()
    with TestClient(app) as c:
        yield c


def register(c, name):
    r = c.post('/api/auth/register', json={'username': name, 'password': 'safePass123'})
    assert r.status_code == 200, r.text
    data = r.json()
    return data['user'], {'Authorization': 'Bearer ' + data['token']}


def befriend(c, user_a, ha, user_b, hb):
    r = c.post('/api/friends/request', headers=ha, json={'player_id': user_b['player_id']})
    assert r.status_code == 200, r.text
    request_id = c.get('/api/friends/requests', headers=hb).json()[0]['id']
    assert c.post(f'/api/friends/accept/{request_id}', headers=hb).status_code == 200


def test_chat_returns_recent_history_and_unread_summary(client):
    a, ha = register(client, 'ChatPerfA')
    b, hb = register(client, 'ChatPerfB')
    befriend(client, a, ha, b, hb)
    conn = db.get_connection()
    try:
        for index in range(250):
            conn.execute('INSERT INTO messages(sender_id,receiver_id,content,is_read) VALUES(?,?,?,0)',
                         (a['id'], b['id'], f'History message {index}'))
        conn.commit()
    finally:
        conn.close()

    unauth = client.get('/api/chat/unread-by-friend')
    assert unauth.status_code == 401
    counts = client.get('/api/chat/unread-by-friend', headers=hb)
    assert counts.status_code == 200, counts.text
    assert counts.json()['counts'] == {str(a['id']): 250}
    assert client.get('/api/chat/unread-by-friend', headers=ha).json()['counts'] == {}

    latest = client.get(f'/api/chat/{a["id"]}/messages', headers=hb)
    assert latest.status_code == 200
    messages = latest.json()
    assert len(messages) == 200
    assert messages[0]['content'] == 'History message 50'
    assert messages[-1]['content'] == 'History message 249'
    assert [m['id'] for m in messages] == sorted(m['id'] for m in messages)

    older = client.get(f'/api/chat/{a["id"]}/messages?offset=200', headers=hb).json()
    assert len(older) == 50
    assert older[0]['content'] == 'History message 0'
    assert older[-1]['content'] == 'History message 49'

    marked = client.post(f'/api/chat/{a["id"]}/read', headers=hb)
    assert marked.status_code == 200
    assert client.get('/api/chat/unread-by-friend', headers=hb).json()['counts'] == {}
    assert client.get(f'/api/chat/{a["id"]}/messages?after_id={messages[-1]["id"]}', headers=hb).json() == []


def test_study_and_teacher_database_initialize_once_and_recover_after_replacement(tmp_path, monkeypatch):
    study_path = tmp_path / 'suite.sqlite3'
    final_path = tmp_path / 'teacher.sqlite3'
    monkeypatch.setattr(study, 'DB', study_path)
    monkeypatch.setattr(final, 'DB', final_path)

    def read_study(_):
        c = study.connect()
        try:
            return c.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
        finally:
            c.close()

    def read_final(_):
        c = final.conn()
        try:
            return c.execute('SELECT COUNT(*) FROM teacher_lessons').fetchone()[0]
        finally:
            c.close()

    with ThreadPoolExecutor(max_workers=6) as pool:
        assert list(pool.map(read_study, range(25))) == [len(study.SEED)] * 25
        assert list(pool.map(read_final, range(25))) == [0] * 25

    assert any(key[0] == str(study_path.resolve()) for key in study._initialized_databases)
    # New database at same path must be initialized too (backup restore/test reset).
    study_path.unlink()
    assert read_study(0) == len(study.SEED)


def test_study_suite_exam_cannot_be_submitted_twice(client, tmp_path, monkeypatch):
    monkeypatch.setattr(study, 'DB', tmp_path / 'study_exam.sqlite3')
    _, headers = register(client, 'StudyPerfUser')
    created = client.post('/api/study-suite/exams', headers=headers, json={'count': 2})
    assert created.status_code == 200, created.text
    exam_id = created.json()['exam_id']
    payload = {'answers': {str(item['id']): '4' for item in created.json()['questions']}}

    def submit(_):
        return client.post(f'/api/study-suite/exams/{exam_id}/submit', headers=headers, json=payload).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(submit, range(2))) == [200, 409]


def test_lan_api_ignores_stale_public_backend_preference():
    import json
    import subprocess
    from pathlib import Path
    config = Path(__file__).resolve().parents[2] / 'js' / 'api-config.js'
    code = r'''
const fs=require('fs'),vm=require('vm');const source=fs.readFileSync(process.argv[1],'utf8');
function load(host, stored, search='') {
 const window={location:{hostname:host,search},localStorage:{getItem:()=>stored}};
 vm.runInNewContext(source,{window,URL,URLSearchParams});return window.MATHWEB_API_URL;
}
console.log(JSON.stringify([
 load('192.168.1.42','https://math-webv2.onrender.com'),
 load('192.168.1.42','http://192.168.1.90:8000'),
 load('192.168.1.42','https://math-webv2.onrender.com','?api=http%3A%2F%2F192.168.1.99%3A8000'),
 load('tralalerotralala2011.github.io',null,'?api=https://evil.invalid'),
]));'''
    result = subprocess.run(['node', '-e', code, str(config)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        'http://192.168.1.42:8000',
        'http://192.168.1.90:8000',
        'http://192.168.1.99:8000',
        'https://math-webv2.onrender.com',
    ]


def test_bulk_presence_returns_only_accepted_friends(client):
    a, ha = register(client, 'PresenceBulkA')
    b, hb = register(client, 'PresenceBulkB')
    c, hc = register(client, 'PresenceBulkC')
    outsider, ho = register(client, 'PresenceOutsider')
    befriend(client, a, ha, b, hb)
    befriend(client, a, ha, c, hc)
    assert client.post('/api/presence/heartbeat', headers=hb).status_code == 200
    assert client.get('/api/presence/friends').status_code == 401
    response = client.get('/api/presence/friends', headers=ha)
    assert response.status_code == 200, response.text
    online = response.json()['online']
    assert set(online) == {str(b['id']), str(c['id'])}
    assert online[str(b['id'])] is True
    assert str(outsider['id']) not in online
    assert client.get('/api/presence/friends', headers=ho).json()['online'] == {}


def test_mixed_question_types_guaranteed_for_partial_ten_question_sets():
    from collections import Counter
    from app.ai.engine.service import AIQuestionService
    expected = {
        1: (1, 0, 0),
        2: (1, 1, 0),
        3: (1, 1, 1),
        5: (3, 1, 1),
        9: (6, 2, 1),
        10: (7, 2, 1),
        20: (14, 4, 2),
    }
    for size, quotas in expected.items():
        for _ in range(20):
            actual = Counter(AIQuestionService.mixed_question_types(size))
            assert tuple(actual[k] for k in ('multiple_choice', 'short_answer', 'true_false')) == quotas


def test_curated_bank_looks_up_requested_topic_not_last_500_of_grade(client):
    from app.ai.engine.service import AIQuestionService
    conn = db.get_connection()
    try:
        # A real bank can have hundreds of newer questions in unrelated topics.
        conn.execute("""INSERT INTO admin_question_bank
            (grade,topic,difficulty,question_type,question,correct_answer,created_at,updated_at)
            VALUES (11,'xac_suat_11','medium','multiple_choice','Valid older bank question','A','now','now')""")
        wanted_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        for i in range(650):
            conn.execute("""INSERT INTO admin_question_bank
                (grade,topic,difficulty,question_type,question,correct_answer,created_at,updated_at)
                VALUES (11,'unrelated_topic','medium','multiple_choice',?,'A','now','now')""", (f'Unrelated {i}',))
        for i in range(510):
            conn.execute("""INSERT INTO admin_question_bank
                (grade,topic,difficulty,question_type,question,correct_answer,created_at,updated_at)
                VALUES (11,'xac_suat_11','hard','multiple_choice',?,'A','now','now')""", (f'Hard {i}',))
        conn.commit()
    finally:
        conn.close()
    candidates = AIQuestionService()._curated_admin_candidates(11, 'xac_suat_11', 'medium', 'multiple_choice')
    assert any(item['id'] == wanted_id for item in candidates)
    assert all(item['topic'] == 'xac_suat_11' and item['difficulty'] == 'medium' for item in candidates)
