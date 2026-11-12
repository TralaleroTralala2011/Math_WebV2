"""Extra real-API regressions for timed-out queues, battles and progress."""
from datetime import datetime, timedelta, timezone
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.matchmaking.routes import init_matchmaking_tables, MATCH_MAX_DURATION_SECONDS
from database import database as db


@pytest.fixture
def client(tmp_path, monkeypatch):
    target = tmp_path / 'audit3.db'
    monkeypatch.setenv('MATHWEB_DB_PATH', str(target))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'ai.sqlite3'))
    monkeypatch.setattr(db, 'DATABASE_PATH', target)
    db.init_database()
    init_matchmaking_tables()
    with TestClient(app) as c:
        yield c


def register(client, name):
    response = client.post('/api/auth/register', json={
        'username': name, 'password': 'safePass123',
    })
    assert response.status_code == 200, response.text
    return response.json()['user'], {'Authorization': 'Bearer ' + response.json()['token']}


def make_battle(client):
    u1, h1 = register(client, 'Round3BattleA')
    u2, h2 = register(client, 'Round3BattleB')
    invite = client.post('/api/matchmaking/invite', headers=h1, json={'player_id': u2['player_id']})
    assert invite.status_code == 200, invite.text
    match_id = invite.json()['match_id']
    assert client.post(f'/api/matchmaking/match/{match_id}/accept', headers=h2).status_code == 200
    assert client.post(f'/api/matchmaking/match/{match_id}/start', headers=h1).status_code == 200
    return match_id, u1, u2, h1, h2


def test_stale_queue_does_not_remain_visible_or_match_to_new_player(client):
    _, h1 = register(client, 'Round3QueueA')
    _, h2 = register(client, 'Round3QueueB')
    settings = {'grade': 10, 'topics': ['menh_de_tap_hop']}
    queued = client.post('/api/matchmaking/random/join', headers=h1, json=settings)
    assert queued.status_code == 200 and queued.json()['status'] == 'QUEUED'
    aged = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    with db.get_connection() as conn:
        conn.execute('UPDATE matchmaking_queue SET created_at=?', (aged,))
    response = client.get('/api/matchmaking/random/status', headers=h1)
    assert response.status_code == 200, response.text
    assert response.json()['status'] == 'IDLE', response.json()
    second = client.post('/api/matchmaking/random/join', headers=h2, json=settings)
    assert second.status_code == 200, second.text
    assert second.json()['status'] == 'QUEUED', second.json()


def test_valid_queue_within_ten_minutes_survives_cleanup(client):
    _, h1 = register(client, 'Round3QueueYoung')
    assert client.post('/api/matchmaking/random/join', headers=h1).status_code == 200
    aged = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    with db.get_connection() as conn:
        conn.execute('UPDATE matchmaking_queue SET created_at=?', (aged,))
    response = client.get('/api/matchmaking/random/status', headers=h1)
    assert response.status_code == 200
    assert response.json()['status'] == 'QUEUED', response.json()


def test_skip_after_timeout_rejected_and_match_finalized_with_score(client):
    match_id, p1, _, h1, h2 = make_battle(client)
    with db.get_connection() as conn:
        match = conn.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        first_question = json.loads(match['questions'])[0]
    answer = client.post(f'/api/matchmaking/match/{match_id}/answer', headers=h1, json={
        'question_index': 0, 'answer': (first_question.get('statement_answers')
                                         if first_question['question_type'] == 'true_false'
                                         else first_question['answer']),
    })
    assert answer.status_code == 200, answer.text
    assert answer.json()['correct'] is True, answer.json()
    aged = (datetime.now(timezone.utc) - timedelta(seconds=MATCH_MAX_DURATION_SECONDS + 10)).isoformat()
    with db.get_connection() as conn:
        conn.execute('UPDATE matches SET started_at=? WHERE id=?', (aged, match_id))
    skip = client.post(f'/api/matchmaking/match/{match_id}/skip', headers=h2,
                       json={'question_index': 0})
    assert skip.status_code == 409, skip.text
    result = client.get(f'/api/matchmaking/match/{match_id}/result', headers=h1)
    assert result.status_code == 200, result.text
    data = result.json()
    assert data['is_finished'] is True
    assert data['player1']['correct'] == 1
    assert data['player2']['correct'] == 0
    assert data['winner_id'] == p1['id']
    assert data['player2']['blank'] == 10
    assert data['player2']['time'] == MATCH_MAX_DURATION_SECONDS


def test_finished_players_time_stays_fixed_during_progress_polling(client):
    match_id, _, _, h1, _ = make_battle(client)
    with db.get_connection() as conn:
        match = conn.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        assert len(json.loads(match['questions'])) == 10
        answers = {str(i): {'correct': False, 'skipped': True, 'answered_at': datetime.now(timezone.utc).isoformat()} for i in range(10)}
        conn.execute('UPDATE matches SET player1_answers=?,player1_current=10,player1_time=? WHERE id=?',
                     (json.dumps(answers), 4.125, match_id))
    response = client.get(f'/api/matchmaking/match/{match_id}/progress', headers=h1)
    assert response.status_code == 200, response.text
    assert abs(response.json()['you']['time'] - 4.125) < 0.0001, response.json()


def test_true_false_battle_grades_four_judgments_not_underlying_answer():
    from app.questions.answer_checker import grade_answer
    from app.matchmaking.routes import sanitize_question
    question = {
        'id': 'tf-demo', 'question_type': 'true_false', 'question': 'Hãy xét bốn nhận định',
        'answer': '1280', 'statements': ['A', 'B', 'C', 'D'],
        'statement_answers': [True, False, True, False],
    }
    safe = sanitize_question(question, 3)
    assert safe['battle_index'] == 3
    assert safe['statements'] == question['statements']
    assert 'answer' not in safe and 'statement_answers' not in safe
    assert grade_answer(question, [True, False, True, False]) is True
    assert grade_answer(question, [True, True, True, False]) is False
    assert grade_answer(question, 'Đúng, Sai, Đúng, Sai') is True


def test_battle_frontend_respects_backend_answer_contract():
    from pathlib import Path
    frontend = (Path(__file__).resolve().parents[2] / 'js/battle.js').read_text(encoding='utf-8')
    from app.matchmaking.routes import MATCH_MAX_DURATION_SECONDS
    assert f'MAX_GAME_TIME_SECONDS: {MATCH_MAX_DURATION_SECONDS},' in frontend
    assert 'question_index: currentQuestionIndex' in frontend
    assert 'const endpoint = skipped ? "skip" : "answer"' in frontend
    assert 'answerQuestion(\n                                option\n                            );' in frontend
    assert 'question.type || question.question_type' in frontend
    assert 'data.player1?.correct' in frontend
    assert 'sendSocketEvent({ type: "progress" })' in frontend
    assert 'type === "sync" && !data.progress' in frontend
    assert 'battle-tf-submit' in frontend
    assert 'mathweb_user' in frontend


def test_legacy_ai_battle_create_requires_real_participants(client):
    a, ha = register(client, 'Round3LegacyA')
    b, hb = register(client, 'Round3LegacyB')
    c, hc = register(client, 'Round3LegacyC')
    request = {
        'player1': str(a['id']), 'player2': str(b['id']), 'grade': 10,
        'player1_topics': ['menh_de_tap_hop'], 'player2_topics': ['menh_de_tap_hop'],
    }
    assert client.post('/api/ai/battle/create', json=request).status_code == 401
    assert client.post('/api/ai/battle/create', json=request, headers=hc).status_code == 403
    response = client.post('/api/ai/battle/create', json=request, headers=ha)
    assert response.status_code == 200, response.text
    assert response.json()['battle_id']
    # Legacy callers may send Player IDs; their rooms are normalized to DB ids.
    request.update(player1=a['player_id'], player2=b['player_id'])
    assert client.post('/api/ai/battle/create', json=request, headers=hb).status_code == 200
