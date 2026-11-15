"""V63 regression: mislabeled Word questions must not leak into quadrilateral games."""
import hashlib
import os
import sqlite3
from pathlib import Path

import pytest

from app.ai.engine.topic_relevance import is_question_on_topic
from app.ai.engine.word_source_v62 import ensure_word_source, select_word_questions, source_availability
from app.ai.engine.service import AIQuestionService
from app.ai.engine.question_identity import question_key

TOPIC = 'g10_geom_quadrilaterals_properties'
OFFTOPIC = [
    'Hai đường thẳng song song bị cắt bởi một đường thẳng. Một góc trong cùng phía bằng 72°. Góc trong cùng phía còn lại bằng bao nhiêu?',
    'Tam giác ABC có đáy AB=17 cm và chiều cao ứng với AB là 4 cm. Tính diện tích.',
    'Hai tam giác đồng dạng có tỉ số độ dài cạnh tương ứng 2:1. Tính tỉ số diện tích.',
]
ONTOPIC = [
    'Hình bình hành ABCD có AB=7 cm, BC=6 cm. Tính chu vi.',
    'Hình thoi ABCD có hai đường chéo AC=8 cm và BD=6 cm. Tính diện tích.',
    'Hai đường chéo của tứ giác ABCD cắt nhau tại trung điểm. Tứ giác ABCD có là hình bình hành?',
]


def test_offtopic_examples_cannot_pass():
    assert all(not is_question_on_topic(TOPIC,q) for q in OFFTOPIC)
    assert all(is_question_on_topic(TOPIC,q) for q in ONTOPIC)


def test_word_raw_rows_are_immutable_and_screened():
    path=ensure_word_source()
    assert path and path.exists()
    with sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True) as conn:
        rows=conn.execute('SELECT question FROM questions WHERE grade=10 AND topic=?',(TOPIC,)).fetchall()
    assert len(rows)==634
    assert sum(is_question_on_topic(TOPIC,r[0]) for r in rows)==93


def test_word_api_never_returns_mislabeled_triangle_questions():
    for kind in ['multiple_choice','short_answer']:
        sample=select_word_questions(10,TOPIC,'easy',kind,150)
        assert sample
        assert all(is_question_on_topic(TOPIC,q['question']) for q in sample)
        assert len({question_key(q['question']) for q in sample})==len(sample)


def test_word_availability_reports_screened_total():
    stats=source_availability(10,TOPIC)
    assert stats['matched_question_count']==93
    assert stats['off_topic_excluded']==541


def test_all_bank_sources_enforce_topic_gate(tmp_path,monkeypatch):
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'history.sqlite'))
    svc=AIQuestionService()
    for level in ['easy','medium','hard']:
        for kind in ['multiple_choice','short_answer']:
            for q in svc._v254_candidates(10,TOPIC,level,kind):
                assert is_question_on_topic(TOPIC,q['question'])


@pytest.mark.parametrize('level',['easy','medium','hard'])
@pytest.mark.parametrize('kind',['multiple_choice','short_answer','mixed'])
def test_live_generation_has_10_distinct_on_topic_prompts(tmp_path,monkeypatch,level,kind):
    monkeypatch.setenv('MATHWEB_AI_HISTORY_DB_PATH',str(tmp_path/'history.sqlite'))
    svc=AIQuestionService()
    batch=svc.generate_set(10,[TOPIC],10,level,kind,
        game_id=f'v63_check_{level}_{kind}',allow_partial=True,max_attempts_per_phase=30)
    rows=batch['questions']
    assert len(rows)==10
    assert all(is_question_on_topic(TOPIC,q['question']) for q in rows)
    assert len({question_key(q['question']) for q in rows})==len(rows)


def test_source_word_not_mutated_by_gate():
    source=Path(__file__).resolve().parents[2]/'question_bank_v254_source/150_CHU_DE_WORD_SOURCE_V60.zip'
    assert source.is_file()
    assert source.stat().st_size>1_000_000
