"""Second-pass regressions for mobile LAN, Battle ordering and speed fairness."""
from __future__ import annotations

import json
from pathlib import Path
from subprocess import run, PIPE

import pytest
from fastapi.testclient import TestClient

from app.main import app
from database import database as db
from app.matchmaking.routes import init_matchmaking_tables, finalize_match_if_needed

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "mathweb_round2.db"
    monkeypatch.setenv("MATHWEB_DB_PATH", str(test_db))
    monkeypatch.setenv("MATHWEB_AI_HISTORY_DB_PATH", str(tmp_path / "history.sqlite3"))
    monkeypatch.setattr(db, "DATABASE_PATH", test_db)
    db.init_database()
    init_matchmaking_tables()
    with TestClient(app) as c:
        yield c


def new_user(client, username):
    res = client.post('/api/auth/register', json={"username": username, "password": "safePass123"})
    assert res.status_code == 200, res.text
    data = res.json()
    return data['user'], {"Authorization": "Bearer " + data['token']}


def make_battle(client):
    player1, h1 = new_user(client, 'BattleFastPlayer')
    player2, h2 = new_user(client, 'BattleSlowPlayer')
    invite = client.post('/api/matchmaking/invite', headers=h1, json={"player_id": player2['player_id']})
    assert invite.status_code == 200, invite.text
    match_id = invite.json()['match_id']
    assert client.post(f'/api/matchmaking/match/{match_id}/accept', headers=h2).status_code == 200
    start = client.post(f'/api/matchmaking/match/{match_id}/start', headers=h1)
    assert start.status_code == 200, start.text
    return match_id, player1, player2, h1, h2


def test_battle_rejects_out_of_order_answer_and_skip(client):
    match_id, _, _, h1, _ = make_battle(client)
    url = f'/api/matchmaking/match/{match_id}'
    assert client.post(url + '/answer', headers=h1, json={"question_index": 2, "answer": "random"}).status_code == 409
    assert client.post(url + '/skip', headers=h1, json={"question_index": 1}).status_code == 409
    first = client.post(url + '/skip', headers=h1, json={"question_index": 0})
    assert first.status_code == 200, first.text
    assert client.post(url + '/skip', headers=h1, json={"question_index": 0}).status_code == 409
    second = client.post(url + '/answer', headers=h1, json={"question_index": 1, "answer": "test"})
    assert second.status_code == 200, second.text
    assert second.json()['current'] == 2


def test_battle_uses_earlier_finishing_player_as_tiebreaker(client):
    match_id, p1, p2, h1, _ = make_battle(client)
    conn = db.get_connection()
    try:
        row = conn.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        questions = json.loads(row['questions'])
        assert len(questions) == 10
        answers = {str(i): {"correct": True, "skipped": False, "answered_at": "2026-11-11T00:00:00+00:00"} for i in range(10)}
        conn.execute('UPDATE matches SET player1_answers=?, player2_answers=?, player1_time=?, player2_time=? WHERE id=?',
                     (json.dumps(answers),json.dumps(answers), 4.25, 7.75, match_id))
        updated = conn.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        completed, winner = finalize_match_if_needed(conn.cursor(), updated, questions)
        conn.commit()
        assert completed is True
        assert winner == p1['id']
        final = conn.execute('SELECT * FROM matches WHERE id=?', (match_id,)).fetchone()
        assert final['status'] == 'FINISHED'
        assert abs(final['player1_time'] - 4.25) < 0.001
        assert abs(final['player2_time'] - 7.75) < 0.001
    finally:
        conn.close()
    result = client.get(f'/api/matchmaking/match/{match_id}/result', headers=h1)
    assert result.status_code == 200, result.text
    assert result.json()['winner_id'] == p1['id']


def test_lan_cors_allows_phone_on_same_wifi(client):
    origin='http://192.168.1.77:5500'
    response=client.options('/api/matchmaking/random/join',headers={
        'Origin':origin,'Access-Control-Request-Method':'POST',
        'Access-Control-Request-Headers':'authorization,content-type'
    })
    assert response.status_code == 200
    assert response.headers.get('access-control-allow-origin') == origin


def test_frontend_api_config_selects_wifi_host_not_public_service():
    code=(ROOT/'js/api-config.js').read_text(encoding='utf-8')
    node_code=r"""
    const fs=require('fs'),vm=require('vm');
    const code=fs.readFileSync(process.argv[1],'utf8');
    function test(host,origin,search='',saved=null){
     const store={getItem:()=>saved};
     const window={location:{hostname:host,origin,search},localStorage:store};
     vm.runInNewContext(code,{window,URLSearchParams,URL});
     return window.MATHWEB_API_URL;
    }
    const got=[
      test('localhost','http://localhost:5500'),
      test('192.168.1.77','http://192.168.1.77:5500'),
      test('10.0.5.12','http://10.0.5.12:5500'),
      test('172.25.1.7','http://172.25.1.7:5500'),
      test('tralalerotralala2011.github.io','https://tralalerotralala2011.github.io','?api=https://bad.example'),
    ];
    console.log(JSON.stringify(got));
    """
    result=run(['node','-e',node_code,str(ROOT/'js/api-config.js')],text=True,stdout=PIPE,stderr=PIPE)
    assert result.returncode==0, result.stderr
    urls=json.loads(result.stdout)
    assert urls==[
        'http://127.0.0.1:8000',
        'http://192.168.1.77:8000',
        'http://10.0.5.12:8000',
        'http://172.25.1.7:8000',
        'https://math-webv2.onrender.com',
    ]


def test_mobile_quick_nav_has_collapsible_accessible_launcher():
    js=(ROOT/'js/quick-navigation.js').read_text(encoding='utf-8')
    css=(ROOT/'css/quick-navigation.css').read_text(encoding='utf-8')
    assert "className='mw-quick-toggle'" in js
    assert "aria-expanded" in js
    assert "'learning-path.html'" in js
    assert "'geometry-studio.html'" in js
    assert "'learn.html'" in js
    assert '.mw-quick-open .mw-quick-links' in css
    assert '#mathweb-quicknav .mw-quick-links{display:none!important}' in css


def test_geometry_usable_offline_and_mobile_measure_panel_foldable():
    html=(ROOT/'geometry-studio.html').read_text(encoding='utf-8')
    assert 'css/geometry-studio-fallback.css' in html
    assert (ROOT/'css/geometry-studio-fallback.css').stat().st_size > 1000
    assert 'id="measure-collapse"' in html
    assert 'id="measure-controls"' in html
    assert "measure-expanded" in html


def test_all_games_have_matching_login_gate_relative_path():
    from html.parser import HTMLParser
    class ScriptSources(HTMLParser):
        def __init__(self):
            super().__init__()
            self.scripts = []
        def handle_starttag(self, tag, attrs):
            if tag == 'script':
                src = dict(attrs).get('src')
                if src: self.scripts.append(src)
    games = sorted((ROOT / 'games').rglob('*.html'))
    assert len(games) == 529
    for path in games:
        parser = ScriptSources()
        parser.feed(path.read_text(encoding='utf-8'))
        scripts = parser.scripts
        depth = len(path.relative_to(ROOT).parts) - 1
        guard = '../' * depth + 'js/protected-pages.js'
        api = '../' * depth + 'js/api-config.js'
        assert guard in scripts, path
        assert api in scripts, path
        assert scripts.index(guard) < scripts.index(api), path
        assert (path.parent / guard).resolve() == (ROOT / 'js/protected-pages.js').resolve()


def test_game_login_redirects_correctly_for_nested_pages():
    code = (ROOT / 'js/protected-pages.js').read_text(encoding='utf-8')
    script = r"""
    const fs=require('fs'),vm=require('vm');const code=fs.readFileSync(process.argv[1],'utf8');
    const cases=[
      ['/site/games/geometry/map.html','../../login.html?next=games%2Fgeometry%2Fmap.html'],
      ['/site/games/knowledge/algebra/1-game.html','../../../login.html?next=games%2Fknowledge%2Falgebra%2F1-game.html'],
      ['/site/account.html','login.html?next=account.html']
    ];
    for(const [pathname,expected] of cases){
      let target=null;
      vm.runInNewContext(code,{location:{pathname,search:'',replace:x=>target=x},localStorage:{getItem:()=>null},Set});
      if(target!==expected)throw Error(pathname+' '+target+' expected '+expected);
    }
    console.log('LOGIN GATES OK');
    """
    result = run(['node','-e',script,str(ROOT/'js/protected-pages.js')],text=True,stdout=PIPE,stderr=PIPE)
    assert result.returncode == 0, result.stderr
