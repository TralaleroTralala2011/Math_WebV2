"""V181: regressions for full website and the QA-gated question bank."""
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app
from app.ai.engine.difficulty import normalize
from app.ai.engine.solver import equivalent
from app.ai.routes import service as ai_service
from database import database as database_module


def test_difficulty_aliases_for_imported_bank():
    assert normalize('foundation') == 'easy'
    assert normalize('intermediate') == 'medium'
    assert normalize('advanced') == 'hard'


def test_untrusted_answers_cannot_trigger_huge_exponents():
    assert equivalent('2^3', '8')
    assert not equivalent('9**9**9', '1')
    assert not equivalent('2**100000000', '1')
    assert not equivalent('sqrt(-1)', '0')


def test_admin_bank_topic_is_filtered_before_limit(tmp_path, monkeypatch):
    db = tmp_path / 'mathweb.db'
    monkeypatch.setattr(database_module, 'DATABASE_PATH', db)
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'ai_history.sqlite3'))
    database_module.init_database()
    conn = database_module.get_connection()
    try:
        stamp = '2026-11-09T00:00:00+00:00'
        def insert(topic, prompt, difficulty='nền tảng', game_id=''):
            conn.execute('''INSERT INTO admin_question_bank
                (grade,topic,difficulty,question_type,game_id,question,choices_json,correct_answer,
                 explanation,source,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                (10, topic, difficulty, 'multiple_choice', game_id, prompt,
                 json.dumps(['1','2','3','4']), '2', 'Giải: 1+1=2.', 'test', stamp, stamp))
        insert('tap_hop', 'Câu hỏi ngân hàng cũ cần truy xuất')
        for i in range(550):
            insert('phuong_trinh', f'Câu hỏi mới không liên quan {i}')
            insert('tap_hop', f'Câu hỏi cùng chủ đề nhưng sai độ khó {i}', 'trung cấp')
        insert('tap_hop', 'Câu hỏi chỉ dành cho trò chơi khác', game_id='different_game')
        conn.commit()
    finally:
        conn.close()
    found = ai_service._curated_admin_candidates(10, 'tap_hop', 'easy', 'multiple_choice')
    assert any(row['question'] == 'Câu hỏi ngân hàng cũ cần truy xuất' for row in found)
    assert all(row['difficulty'] == 'nền tảng' for row in found)
    assert all(not row['game_id'] for row in found)


def test_ai_practice_can_retrieve_and_grade_curated_bank(tmp_path, monkeypatch):
    db = tmp_path / 'mathweb.db'
    monkeypatch.setattr(database_module, 'DATABASE_PATH', db)
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH', str(tmp_path / 'ai_history.sqlite3'))
    database_module.init_database()
    conn = database_module.get_connection()
    try:
        stamp = '2026-11-09T00:00:00+00:00'
        conn.execute('''INSERT INTO admin_question_bank
            (grade,topic,difficulty,question_type,question,choices_json,correct_answer,
             explanation,source,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
            (10,'tap_hop','nền tảng','multiple_choice',
             'Một tập hợp có 3 phần tử. Tập đó có bao nhiêu tập con?',
             json.dumps(['6','7','8','9']), '8',
             'Bước 1: Một tập n phần tử có 2^n tập con. Bước 2: Thay n=3, được 8 tập con.',
             'V181 test',stamp,stamp))
        conn.commit()
    finally:
        conn.close()
    # The API must return the actual saved question, not merely show it in Admin.
    with TestClient(app) as client:
        response = client.post('/api/ai/questions', json={
            'grade':10, 'topics':['tap_hop'], 'count':1,
            'difficulty':'easy', 'question_type':'multiple_choice',
        })
        assert response.status_code == 200, response.text
        item = response.json()['questions'][0]
        assert item.get('source') == 'V181 test'
        assert item['answer'] == '8'
        answer = client.post(f'/api/ai/questions/{item["id"]}/answer', json={'answer':'C'})
        assert answer.status_code == 200, answer.text
        assert answer.json()['correct'] is True
