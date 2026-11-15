"""Regression checks for V61 Word provenance and topic routing.

These tests never write user data or regenerate question banks.
"""
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path
from app.ai.engine.knowledge_service import KnowledgeService

ROOT=Path(__file__).resolve().parents[2]
STORAGE=ROOT/'backend/app/ai/storage'
MAPPING=STORAGE/'v254_b56_topic_map.json'
SOURCE=ROOT/'question_bank_v254_source/150_CHU_DE_WORD_SOURCE_V60.zip'
CORRECTED=ROOT/'question_bank_v254_source/150_CHU_DE_WORD_CORRECTED_V61.zip'


def test_150_word_files_exactly_match_original_bytes():
    mapping=json.loads(MAPPING.read_text(encoding='utf8'))
    assert len(mapping)==150
    with zipfile.ZipFile(SOURCE) as old,zipfile.ZipFile(CORRECTED) as new:
        assert len([x for x in old.namelist() if x.endswith('.docx')])==150
        assert len([x for x in new.namelist() if x.endswith('.docx')])==150
        assert new.testzip() is None
        for entry in mapping.values():
            assert old.read(entry['source_word_legacy'])==new.read(entry['source_word'])


def test_word_topic_ids_route_by_both_old_and_corrected_filenames():
    knowledge=KnowledgeService()
    mapping=json.loads(MAPPING.read_text(encoding='utf8'))
    for entry in mapping.values():
        for filename in (entry['source_word'],entry['source_word_legacy']):
            assert knowledge.normalize_topics(entry['grade'],[filename])==[entry['topic']]
            assert knowledge.normalize_topics(entry['grade'],[filename.rsplit('/',1)[-1]])==[entry['topic']]


def test_ambiguous_display_names_never_guess_wrong_topic():
    knowledge=KnowledgeService()
    assert knowledge.normalize_topics(11,['Dãy số'])==[]
    assert knowledge.normalize_topics(11,['Phương trình lượng giác'])==[]
    assert knowledge.normalize_topics(11,['day_so'])==['day_so']
    assert knowledge.normalize_topics(11,['day_so_tong_quat'])==['day_so_tong_quat']


def test_sqlite_seed_matches_manifest_and_provenance():
    mapping=json.loads(MAPPING.read_text(encoding='utf8'))
    expected={(int(v['grade']),v['topic']):v['source_word'] for v in mapping.values()}
    manifest=json.loads((STORAGE/'v60_word_manifest.json').read_text(encoding='utf8'))
    db_path=STORAGE/'v60_word_candidates.sqlite'
    assert db_path.stat().st_size==manifest['db_bytes']
    assert hashlib.sha256(db_path.read_bytes()).hexdigest()==manifest['db_sha256']
    with sqlite3.connect(f'file:{db_path.as_posix()}?mode=ro',uri=True) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        for grade,topic,path in db.execute('SELECT DISTINCT grade,topic,source_word FROM questions'):
            assert expected[(grade,topic)]==path
    with zipfile.ZipFile(STORAGE/'v60_word_candidates.seed.zip') as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read('v60_word_candidates.sqlite')).hexdigest()==manifest['db_sha256']
