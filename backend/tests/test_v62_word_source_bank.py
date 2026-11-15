"""Regression gates for source-faithful 150 Word -> indexed runtime question bank.

Does not mutate production/user SQLite files.
"""
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path

import pytest

from app.ai.engine.question_identity import question_key
from app.ai.engine.word_source_v62 import ensure_word_source, select_word_questions, source_availability
from app.ai.engine.service import AIQuestionService

ROOT = Path(__file__).resolve().parents[2]
STORAGE = ROOT / 'backend/app/ai/storage'
MAP = json.loads((STORAGE/'v254_b56_topic_map.json').read_text(encoding='utf8'))
MANIFEST = json.loads((STORAGE/'v62_word_source_manifest.json').read_text(encoding='utf8'))
SOURCE = ROOT/'question_bank_v254_source/150_CHU_DE_WORD_SOURCE_V60.zip'


def test_uploaded_150_word_source_has_identical_bytes_and_checksum():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == MANIFEST['source_sha256']
    with zipfile.ZipFile(SOURCE) as archive:
        assert len([n for n in archive.namelist() if n.endswith('.docx')]) == 150
        assert archive.testzip() is None


def test_indexed_bank_integrity_and_all_topic_coverage():
    path = ensure_word_source()
    assert path is not None
    assert path.stat().st_size == MANIFEST['db_bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == MANIFEST['db_sha256']
    with sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert db.execute('SELECT COUNT(*) FROM questions').fetchone()[0] == MANIFEST['usable_questions']
        expected={(v['grade'],v['topic']):v['source_word'] for v in MAP.values()}
        assert len(expected)==150
        for grade,topic,source_word in db.execute('SELECT DISTINCT grade,topic,source_word FROM questions'):
            assert expected[(grade,topic)] == source_word
        assert db.execute('SELECT COUNT(*) FROM (SELECT grade,topic FROM questions GROUP BY grade,topic)').fetchone()[0] == 150
        assert db.execute('SELECT COUNT(DISTINCT prompt_hash) FROM questions').fetchone()[0] == MANIFEST['usable_questions']


def test_all_150_jsonl_exports_match_exact_topic_and_source():
    for number,topic in MAP.items():
        f=ROOT/'question_bank_word_v62'/f'{int(number):03d}_toan_{topic["grade"]}_{topic["topic"]}.jsonl'
        assert f.is_file(),f
        with f.open(encoding='utf8') as inp:
            first=json.loads(next(inp))
            assert first['grade'] == topic['grade']
            assert first['topic'] == topic['topic']
            assert first['source_word'] == topic['source_word']


def test_read_api_exact_topic_grade_level_and_type():
    for grade,topic,difficulty,kind in [
        (10,'bai_toan_thuc_te_10','easy','short_answer'),
        (10,'ham_so','medium','multiple_choice'),
        (11,'day_so','medium','multiple_choice'),
        (12,'cuc_tri','medium','multiple_choice'),
    ]:
        rows=select_word_questions(grade,topic,difficulty,kind,30)
        assert rows
        assert len(rows)<=30
        assert all(r['question_type']==kind and r['difficulty']==difficulty for r in rows)
        assert len({question_key(r['question']) for r in rows})==len(rows)
    assert select_word_questions(10,'toa_do_khong_gian','medium','multiple_choice') == []
    assert select_word_questions(12,'cuc_tri','easy','true_false') == []


def test_shared_bank_source_is_prioritized_and_deduped():
    svc=AIQuestionService()
    rows=svc._v254_candidates(12,'cuc_tri','medium','multiple_choice')
    assert rows and all(row['id'].startswith('word62_') for row in rows)
    assert len({question_key(x['question']) for x in rows})==len(rows)


def test_10_questions_in_practice_from_word_without_repeats(monkeypatch,tmp_path):
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'ai_history.sqlite'))
    svc=AIQuestionService()
    for grade,topic in [(10,'ham_so'),(11,'day_so'),(12,'cuc_tri')]:
        data=svc.generate_set(grade,[topic],10,'medium','multiple_choice',max_attempts_per_phase=3)
        questions=data['questions']
        assert len(questions)==10
        assert all(q['grade']==grade and q['topic']==topic for q in questions)
        assert all(q['source']=='150_CHU_DE_WORD' for q in questions)
        assert len(set(question_key(q['question']) for q in questions))==10


def test_battle_uses_word_bank_without_repeated_prompts():
    from app.matchmaking.routes import generate_ai_battle_questions
    questions=generate_ai_battle_questions(11,['day_so'],'medium','multiple_choice',count=10)
    assert len(questions)==10
    assert len({question_key(q['question']) for q in questions})==10
    assert all(q['source']=='150_CHU_DE_WORD' for q in questions)


def test_availability_has_no_question_or_answer_data():
    output=source_availability(10,'ham_so')
    assert output['available'] and output['matched_question_count']>0
    for item in output['topics']:
        assert 'answer' not in item
        assert 'question' not in item


def test_sqlite_recovery_seed_hash():
    with zipfile.ZipFile(STORAGE/'v62_word_source.seed.zip') as z:
        assert z.namelist()==['v62_word_source.sqlite']
        assert z.testzip() is None
        assert hashlib.sha256(z.read('v62_word_source.sqlite')).hexdigest()==MANIFEST['db_sha256']


def test_read_only_bank_can_recover_from_signed_seed_without_user_database_changes(monkeypatch,tmp_path):
    import app.ai.engine.word_source_v62 as module
    monkeypatch.setattr(module,'DB_FILE',tmp_path/'nonexistent.sqlite')
    monkeypatch.setenv('MATHWEB_WORD_SOURCE_CACHE',str(tmp_path/'cache'))
    module.ensure_word_source.cache_clear()
    try:
        recovered=module.ensure_word_source()
        assert recovered is not None and recovered.is_file()
        assert recovered.parent == tmp_path/'cache'
        assert hashlib.sha256(recovered.read_bytes()).hexdigest()==MANIFEST['db_sha256']
    finally:
        module.ensure_word_source.cache_clear()
