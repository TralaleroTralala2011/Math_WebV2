"""V59 regression tests: additive bank and source preservation."""
from pathlib import Path
import collections
import hashlib
import json
import sqlite3
import zipfile

ROOT = Path(__file__).resolve().parents[2]
STORAGE = ROOT/'backend/app/ai/storage'


def test_v59_additions_have_unique_prompts_and_170_checked_answers():
    from app.ai.engine.v59_bank import ensure_v59_bank
    from app.ai.engine.validator import validate
    file = ensure_v59_bank()
    assert file and file.exists()
    data = json.loads((STORAGE/'v59_screened_additions_manifest.json').read_text('utf8'))
    assert data['counts']['original_answer_checked_added']==170
    assert data['counts']['b56_screened_added']>=2300
    assert data['counts']['overlay_total']==sum([
        data['counts']['original_answer_checked_added'],data['counts']['b56_screened_added']])
    assert hashlib.sha256(file.read_bytes()).hexdigest()==data['sha256']
    with sqlite3.connect(f'file:{file.resolve()}?mode=ro',uri=True) as conn:
        all_q=conn.execute('SELECT question FROM questions').fetchall()
        assert len(all_q)==data['counts']['overlay_total']
        norm=lambda s:' '.join(s.lower().split())
        assert len({norm(q[0]) for q in all_q})==len(all_q)
        generated=conn.execute('SELECT id,grade,topic,difficulty,question_type,question,answer,solution,options,form_id FROM questions WHERE source="V59_generated_independently_calculated"').fetchall()
        assert len(generated)==170
        forms=collections.Counter(row[9] for row in generated)
        assert len(forms)==17 and set(forms.values())=={10}
        for id,grade,topic,difficulty,qt,question,answer,solution,opts,form_id in generated:
            obj=dict(id=id,grade=grade,topic=topic,difficulty=difficulty,question_type=qt,question=question,answer=answer,solution=solution,options=json.loads(opts))
            validate(obj)
            assert len(solution)>=55
    with sqlite3.connect(f'file:{(STORAGE/"v254_candidates.sqlite").resolve()}?mode=ro',uri=True) as conn:
        old={norm(q[0]) for q in conn.execute('SELECT question FROM questions')}
    assert not (old & {norm(q[0]) for q in all_q})


def test_v59_bank_source_zips_preserved_exactly():
    src=ROOT/'question_bank_v254_source/Question_Bank_V254_B56_BO_SUNG_CO_KIEM_TRA.zip'
    assert src.exists()
    with zipfile.ZipFile(src) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.endswith('.docx')])==150
    # Existing V254/B56 tables were never modified by the overlay builder.
    for filename in ('v254_candidates.sqlite','v254_b56_candidates.sqlite'):
        with sqlite3.connect(f'file:{(STORAGE/filename).resolve()}?mode=ro',uri=True) as conn:
            assert conn.execute('PRAGMA quick_check').fetchone()[0]=='ok'


def test_v59_service_filters_duplicates_and_excludes_mislabeled_answers():
    from app.ai.engine.service import AIQuestionService
    svc=AIQuestionService()
    for grade,topic in ((10,'chia_du'),(10,'phuong_trinh_bac_hai'),(11,'cap_so_cong'),(12,'pt_mu')):
        rows=svc._v254_candidates(grade,topic,'medium','short_answer')
        assert rows, (grade,topic)
        assert len({' '.join(row['question'].casefold().split()) for row in rows})==len(rows)
        assert all(not str(row['answer']).startswith(('A.','B.','C.','D.')) for row in rows)


def test_v59_atomic_restoration_and_corruption_recovery(tmp_path,monkeypatch):
    from app.ai.engine import v59_bank
    dest=tmp_path/'v59_screened_additions.sqlite'
    for name in ('v59_screened_additions.seed.zip','v59_screened_additions_manifest.json'):
        (tmp_path/name).write_bytes((STORAGE/name).read_bytes())
    dest.write_bytes(b'not a database')
    monkeypatch.setattr(v59_bank,'_STORAGE',tmp_path)
    monkeypatch.setattr(v59_bank,'_READY',False)
    restored=v59_bank.ensure_v59_bank()
    assert restored==dest
    with sqlite3.connect(f'file:{dest}?mode=ro',uri=True) as conn:
        assert conn.execute('PRAGMA quick_check').fetchone()[0]=='ok'


def test_all_150_canonical_topics_have_candidate_rows():
    from app.ai.engine.knowledge_service import KnowledgeService
    catalogue=KnowledgeService()
    expected={(int(grade),x['id']) for grade,rows in catalogue.data.items() for x in rows}
    old=sqlite3.connect(f"file:{(STORAGE/'v254_candidates.sqlite').resolve()}?mode=ro",uri=True)
    overlay=sqlite3.connect(f"file:{(STORAGE/'v59_screened_additions.sqlite').resolve()}?mode=ro",uri=True)
    try:
        covered={(g,t) for g,t in old.execute('select distinct grade,topic from questions')}
        covered.update({(g,t) for g,t in overlay.execute('select distinct grade,topic from questions')})
        assert len(expected)==150
        assert not (expected-covered),sorted(expected-covered)
    finally:
        old.close();overlay.close()
