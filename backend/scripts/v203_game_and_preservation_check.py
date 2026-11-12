#!/usr/bin/env python3
"""Verify new curated bank availability to practice/Battle and unchanged non-bank data."""
import sqlite3,sys,json,hashlib,collections
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(BASE/'backend'))
from app.ai.engine.service import AIQuestionService
from app.ai.engine.validator import validate
from app.questions.answer_checker import grade_answer
DB=BASE/'backend/database/mathweb.db';BASELINE=BASE/'bank_updates/V198_before_import_backup.sqlite'
versions=tuple(f'V{x}' for x in range(198,204));ai=AIQuestionService();fails=[];checks=0;seen=set()
for version in versions:
 specs=json.loads((BASE/'bank_updates'/f'{version}_FAMILY_SPECS.json').read_text())
 for f in specs:
  grade,topic=f['grade'],f['topic'];difficulty={'nền tảng':'easy','trung cấp':'medium','nâng cao':'hard'}[f['difficulty']]
  for typ in ('multiple_choice','short_answer','true_false'):
   for game in ('boc_bi','battle'):
    key=(version,grade,topic,difficulty,typ,game)
    if key in seen:continue
    seen.add(key)
    items=ai._curated_admin_candidates(grade,topic,difficulty,typ,game_id=game)
    eligible=[x for x in items if x['source'].startswith(version+' ')]
    if not eligible:
     fails.append({'version':version,'grade':grade,'topic':topic,'format':typ,'game':game,'reason':'missing from curated reader'});continue
    q=ai._build_curated_question(eligible[0],grade,topic,difficulty,typ)
    if not q:
     fails.append({'version':version,'grade':grade,'topic':topic,'format':typ,'game':game,'reason':'could not build'});continue
    try:
     validate(q);assert grade_answer(q,q['answer'])
     if typ=='multiple_choice':assert sum(bool(grade_answer(q,c)) for c in q['options'])==1
     if typ=='true_false':assert len(q['statements'])==4
    except Exception as exc:
     fails.append({'version':version,'grade':grade,'topic':topic,'format':typ,'game':game,'reason':str(exc)});continue
    checks+=1
assert checks==141*3*2,(checks,len(fails))
old=sqlite3.connect(BASELINE);new=sqlite3.connect(DB)
exclude={'admin_question_bank','sqlite_sequence','mathweb_bank_import_ledger','mathweb_v198_topic_repair_ledger'}
content_checks={}
for (tb,) in old.execute("SELECT name FROM sqlite_master WHERE type='table'"):
 if tb in exclude or tb.startswith('sqlite_'):continue
 def hash_table(conn):
  h=hashlib.sha256();c=0
  for row in conn.execute('SELECT key,value FROM database_metadata ORDER BY key' if tb=='database_metadata' else f'SELECT * FROM "{tb}" ORDER BY rowid'):
   h.update(json.dumps(list(row),ensure_ascii=False,default=str,sort_keys=True).encode('utf8'));h.update(b'\n');c+=1
  return (c,h.hexdigest())
 o,n=hash_table(old),hash_table(new);content_checks[tb]={'rows_before':o[0],'rows_after':n[0],'sha256_before':o[1],'sha256_after':n[1],'equal':o==n}
assert all(r['equal'] for r in content_checks.values()),[x for x in content_checks if not content_checks[x]['equal']]
report={'version':'V203','families':141,'test_matrix':{'practice_and_battle_by_family_and_format':141*3*2,'passed':checks,'failed':fails},'nonbank_tables_content_unchanged':len(content_checks),'metadata_timestamp_note':'database_metadata.updated_at changes on application connection, while schema_version key/value are unchanged','nonbank_content_checks':content_checks,'production_verified':False,'limitations':'Games inspected through curated loading/building path only; no external live UI deployment.'}
(BASE/'bank_updates/V203_GAME_AND_PRESERVATION_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ('nonbank_content_checks',)},ensure_ascii=False))
assert not fails
