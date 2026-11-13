"""Five-minute continuous Battle contract: no runtime question generation."""
from test_api_integration import client, register
from app.matchmaking.routes import MATCH_MAX_DURATION_SECONDS, generate_ai_battle_questions


def test_five_minute_duration():
    assert MATCH_MAX_DURATION_SECONDS == 300


def test_battle_questions_are_existing_bank_records(monkeypatch):
    from app.matchmaking.routes import ai_service
    def no_generator(*args, **kwargs):
        raise AssertionError('Battle must never invoke the AI generator')
    monkeypatch.setattr(ai_service, 'generate_set', no_generator)
    monkeypatch.setattr(ai_service.generator, 'generate', no_generator)
    deck = generate_ai_battle_questions(10, ['menh_de_tap_hop'], 'easy', 'multiple_choice')
    assert deck and len(deck) == 10
    assert all(q.get('source') == 'Question_Bank_V254' or q.get('admin_question_id') for q in deck)


def test_bank_deck_extends_after_ten_questions(client):
    _, a = register(client, 'V37BattleA')
    b_user, b = register(client, 'V37BattleB')
    invitation = client.post('/api/matchmaking/invite', headers=a, json={
        'player_id': b_user['player_id'], 'grade':10,
        'topics':['menh_de_tap_hop'], 'difficulty':'easy',
        'question_type':'multiple_choice'})
    assert invitation.status_code == 200, invitation.text
    mid = invitation.json()['match_id']
    assert client.post(f'/api/matchmaking/match/{mid}/accept', headers=b).status_code == 200
    assert client.post(f'/api/matchmaking/match/{mid}/start', headers=a).status_code == 200
    for i in range(10):
        r=client.post(f'/api/matchmaking/match/{mid}/skip',headers=a,json={'question_index':i})
        assert r.status_code == 200, r.text
        assert not r.json().get('finished'), 'Do not finish after initial 10 questions'
    nxt=client.get(f'/api/matchmaking/match/{mid}',headers=a)
    assert nxt.status_code == 200, nxt.text
    data=nxt.json()
    assert data['status']=='PLAYING'
    assert len(data['questions'])>10
    prompts=[q['question'] for q in data['questions']]
    assert len(prompts)==len(set(prompts))
