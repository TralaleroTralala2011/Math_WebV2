#!/usr/bin/env python3
"""Smoke all new V192 topic+format combinations via the REAL application's SQLite reader.
For QA only, not proof that all historical records have correct mathematical solutions.
"""
import sys,json,sqlite3,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))
from app.ai.engine.service import AIQuestionService
from app.ai.engine.validator import validate
from app.questions.answer_checker import grade_answer
from database.database import DATABASE_PATH
TAGS=ROOT/'bank_updates/V192_FAMILY_SPECS.json'
REPORT=ROOT/'bank_updates/V192_FULL_TOPIC_RETRIEVAL_TEST.json'

def run():
 db=ROOT/'backend/database/mathweb.db'
 assert db.resolve()==DATABASE_PATH.resolve(),(db,DATABASE_PATH)
 specs=json.loads(TAGS.read_text(encoding='utf8'))
 assert len(specs)==150
 ai=AIQuestionService();results=[];fails=[]
 for sp in specs:
  level={'nền tảng':'easy','trung cấp':'medium','nâng cao':'hard'}[sp['difficulty']]
  for fmt in ('multiple_choice','short_answer','true_false'):
   found=ai._curated_admin_candidates(sp['grade'],sp['topic'],level,fmt)
   new=[item for item in found if str(item.get('source','')).startswith('V192')]
   if not new:
    fails.append((sp['key'],level,fmt,'no v192 row'));continue
   q=ai._build_curated_question(new[0],sp['grade'],sp['topic'],level,fmt)
   if not q:
    fails.append((sp['key'],level,fmt,'build none'));continue
   try:
    validate(q)
    assert grade_answer(q,q['answer']),(sp['key'],fmt,'grade failed')
    if fmt=='multiple_choice':
     assert sum(bool(grade_answer(q,option)) for option in q['options'])==1
    if fmt=='true_false': assert len(q.get('statements',[]))==4
   except Exception as e:
    fails.append((sp['key'],level,fmt,str(e)));continue
   results.append((sp['grade'],sp['topic'],fmt))
 report={'scenario':'local bundled SQLite DB, not live production',
  'catalog_topics_tested':len(specs),'topic_format_pairs_expected':len(specs)*3,
  'topic_format_pairs_passed':len(results),'failed':fails,
  'question_types':dict(collections.Counter(fmt for _,_,fmt in results)),
  'per_grade':dict(collections.Counter(str(g) for g,_,_ in results)),
  'grade_and_answer_equivalence_tested':True,
  'production_verified':False}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='failed'},ensure_ascii=False))
 assert not fails,fails[:15]
if __name__=='__main__':run()
