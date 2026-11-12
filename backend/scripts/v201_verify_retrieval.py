#!/usr/bin/env python3
"""Local SQLite staging smoke for V201 newly integrated questions, all formats."""
import collections,json,sqlite3,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'backend'))
from app.ai.engine.service import AIQuestionService
from app.ai.engine.validator import validate
from app.questions.answer_checker import grade_answer
from database.database import DATABASE_PATH


def main():
    specs=json.loads((BASE/'bank_updates/V201_FAMILY_SPECS.json').read_text())
    assert DATABASE_PATH.resolve()==(BASE/'backend/database/mathweb.db').resolve()
    ai=AIQuestionService();fails=[];passed=[]
    for family in specs:
        g,t=family['grade'],family['topic']
        level={'nền tảng':'easy','trung cấp':'medium','nâng cao':'hard'}[family['difficulty']]
        for typ in ['multiple_choice','short_answer','true_false']:
            items=ai._curated_admin_candidates(g,t,level,typ)
            candidates=[x for x in items if str(x['source']).startswith('V201')]
            if not candidates:
                fails.append({'form':family['form_id'],'format':typ,'why':'not retrievable'});continue
            built=ai._build_curated_question(candidates[0],g,t,level,typ)
            if not built:
                fails.append({'form':family['form_id'],'format':typ,'why':'could not build'});continue
            try:
                validate(built)
                assert grade_answer(built,built['answer'])
                if typ=='multiple_choice':
                    assert sum(bool(grade_answer(built,x)) for x in built['options'])==1
                if typ=='true_false':
                    assert len(built['statements'])==4
            except Exception as e:
                fails.append({'form':family['form_id'],'format':typ,'why':str(e)});continue
            passed.append({'form':family['form_id'],'format':typ,'topic':t})
    with sqlite3.connect(BASE/'backend/database/mathweb.db') as db:
        rows=db.execute("select count(*) from admin_question_bank where source='V201 QA-gated'").fetchone()[0]
        bank_total=db.execute('select count(*) from admin_question_bank').fetchone()[0]
        qc=db.execute('pragma quick_check').fetchone()[0]
        topic_unmatched=db.execute("select grade,topic,count(*) from admin_question_bank where source='V201 QA-gated' group by grade,topic").fetchall()
    result={'V201_inserted_rows':rows,'bank_total':bank_total,'qa_pairs_expected':len(specs)*3,'qa_pairs_passed':len(passed),'failed':fails,'sqlite_integrity':qc,'formats':dict(collections.Counter(r['format'] for r in passed)),'provenance':'bundled local SQLite; no production access','production_verified':False}
    (BASE/'bank_updates/V201_RETRIEVAL_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='failed'},ensure_ascii=False))
    assert not fails,fails[:20]
    assert rows==len(specs)*10

if __name__=='__main__':main()
