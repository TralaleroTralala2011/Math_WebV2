"""V48: real routes tested with two independent learner tokens and a temporary DB.
The read-only bundled V254 draft bank is checked separately from approved exam data.
"""
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.matchmaking.routes import init_matchmaking_tables, generate_ai_battle_questions
from app.ai.routes import service
from database import database as db


@pytest.fixture
def client(tmp_path, monkeypatch):
    path = tmp_path / 'v48_users.sqlite'
    monkeypatch.setenv('MATHWEB_DB_PATH', str(path))
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'v48_history.sqlite'))
    monkeypatch.setattr(db, 'DATABASE_PATH', path)
    db.init_database()
    init_matchmaking_tables()
    with TestClient(app) as c:
        yield c


def make_user(client, username):
    r = client.post('/api/auth/register', json={'username': username, 'password': 'TestPass987!0'})
    assert r.status_code == 200, r.text
    return r.json()['user'], {'Authorization': 'Bearer ' + r.json()['token']}


def test_random_matching_three_grade_pools_and_shared_question_deck(client):
    users = [make_user(client, f'V48Random{i}') for i in range(4)]
    x, hx = users[0]
    y, hy = users[1]
    z, hz = users[2]
    w, hw = users[3]
    grade10 = {'grade': 10, 'topics': ['menh_de_tap_hop'], 'difficulty': 'medium', 'question_type': 'mixed'}
    grade11 = {'grade': 11, 'topics': ['cap_so_cong'], 'difficulty': 'medium', 'question_type': 'mixed'}
    assert client.post('/api/matchmaking/random/join', json=grade10, headers=hx).json()['status'] == 'QUEUED'
    assert client.post('/api/matchmaking/random/join', json=grade11, headers=hz).json()['status'] == 'QUEUED'
    r = client.post('/api/matchmaking/random/join', json=grade10, headers=hy)
    assert r.status_code == 200, r.text
    assert r.json()['status'] == 'MATCHED'
    mid = r.json()['match_id']
    for h in (hx, hy):
        match = client.get(f'/api/matchmaking/match/{mid}', headers=h)
        assert match.status_code == 200, match.text
        body = match.json()
        assert body['grade'] == 10
        assert len(body['questions']) >= 1
        assert not any('answer' in q or 'solution' in q for q in body['questions'])
    assert client.get('/api/matchmaking/random/status', headers=hz).json()['status'] == 'QUEUED'
    r11 = client.post('/api/matchmaking/random/join', json=grade11, headers=hw)
    assert r11.status_code == 200 and r11.json()['status'] == 'MATCHED'
    assert r11.json()['match_id'] != mid


def test_player_id_and_friend_invite_works_without_online_flag(client):
    a, ha = make_user(client, 'V48InviteA')
    b, hb = make_user(client, 'V48InviteB')
    find = client.get('/api/matchmaking/player', params={'player_id': b['player_id']}, headers=ha)
    assert find.status_code == 200 and find.json()['player_id'] == b['player_id']
    request = client.post('/api/friends/request', json={'player_id': b['player_id']}, headers=ha)
    assert request.status_code == 200, request.text
    incoming = client.get('/api/friends/requests', headers=hb)
    assert incoming.status_code == 200 and len(incoming.json()) == 1
    accepted = client.post('/api/friends/accept/' + str(incoming.json()[0]['id']), headers=hb)
    assert accepted.status_code == 200, accepted.text
    friends = client.get('/api/friends', headers=ha)
    assert friends.status_code == 200
    assert any(x['player_id'] == b['player_id'] for x in friends.json())
    send = client.post('/api/matchmaking/invite', headers=ha, json={
        'player_id': b['player_id'], 'grade': 11, 'topics': ['cap_so_cong'],
        'difficulty':'medium', 'question_type':'mixed'
    })
    assert send.status_code == 200, send.text
    mid = send.json()['match_id']
    received = client.get('/api/matchmaking/invites', headers=hb)
    assert received.status_code == 200 and received.json()
    assert client.post(f'/api/matchmaking/match/{mid}/accept', headers=hb).status_code == 200
    details = client.get(f'/api/matchmaking/match/{mid}', headers=ha)
    assert details.status_code == 200 and details.json()['grade'] == 11


def test_battle_bank_uses_existing_decks_and_never_mutates_bank(monkeypatch):
    # Using a seeded archive rather than an output of the runtime generator.
    def forbidden(*args, **kwargs):
        raise AssertionError('Battle should not generate new questions while starting a room')
    monkeypatch.setattr(service, 'generate_set', forbidden)
    for grade in (10, 11, 12):
        topic = service.topics(grade)[0]['id']
        deck = generate_ai_battle_questions(grade, [topic], 'medium', 'mixed')
        assert deck, (grade, topic)
        assert len({q['question'] for q in deck}) == len(deck)
        assert all(q['grade'] == grade and q['topic'] == topic for q in deck)
        assert all(q.get('source') == 'Question_Bank_V254' or q.get('admin_question_id') for q in deck)
        assert all(q.get('solution') and q.get('answer') for q in deck)
        assert all(q.get('bank_status') == 'candidate_unverified' for q in deck if q.get('source') == 'Question_Bank_V254')


def test_v254_manifest_counts_are_not_claimed_as_certified():
    from app.ai.engine.service import AIQuestionService
    base = Path(__file__).resolve().parents[1] / 'app' / 'ai' / 'storage'
    manifest = json.loads((base / 'v254_seed_manifest.json').read_text(encoding='utf-8'))
    assert manifest['questions'] == 83298
    assert manifest['source']
    conn = sqlite3.connect(f"file:{(base/'v254_candidates.sqlite').as_posix()}?mode=ro", uri=True)
    try:
        actual = conn.execute('select count(*) from questions').fetchone()[0]
        assert actual == manifest['questions']
        assert conn.execute('select count(distinct grade || ":" || topic) from questions').fetchone()[0] == 147
    finally:
        conn.close()


def test_v254_can_restore_from_packaged_seed_without_user_database(tmp_path, monkeypatch):
    import shutil
    from app.ai.engine import v254_bank
    source_dir = Path(__file__).resolve().parents[1] / 'app' / 'ai' / 'storage'
    for name in ('v254_candidates.seed.zip', 'v254_seed_manifest.json'):
        shutil.copy2(source_dir / name, tmp_path / name)
    monkeypatch.setattr(v254_bank, '_BANK_DIR', tmp_path)
    restored = v254_bank.ensure_v254_bank()
    assert restored == tmp_path / 'v254_candidates.sqlite'
    assert restored.is_file()
    with sqlite3.connect(f'file:{restored.as_posix()}?mode=ro', uri=True) as db:
        assert db.execute('SELECT count(*) FROM questions').fetchone()[0] == 83298
    assert v254_bank.ensure_v254_bank() == restored


def test_learning_and_roadmap_optional_bank_practice(client):
    for grade, topic in ((10, 'menh_de_tap_hop'), (11, 'cap_so_cong'), (12, 'ung_dung_dao_ham')):
        response = client.post('/api/ai/practice/session', json={
            'grade': grade, 'topics': [topic], 'count': 2,
            'difficulty':'medium', 'question_type':'multiple_choice'
        })
        assert response.status_code == 200, response.text
        result = response.json()
        assert len(result['questions']) == 2
        q = result['questions'][0]
        assert q['grade'] == grade and q['topic'] == topic
        assert len(q.get('options') or []) == 4
        checked = client.post('/api/ai/questions/'+q['id']+'/answer', json={'answer':q['answer']})
        assert checked.status_code == 200, checked.text
        assert checked.json()['correct'] is True
        assert checked.json()['solution']


def test_learning_and_roadmap_have_additive_bank_panel():
    root = Path(__file__).resolve().parents[2]
    for page in ('learn.html', 'learning-path.html'):
        content = (root / page).read_text(encoding='utf-8')
        assert 'mw-learning-bank-v48.js' in content
        assert 'mw-learning-bank-v48.css' in content
