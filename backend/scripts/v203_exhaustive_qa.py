#!/usr/bin/env python3
"""Exhaustive app-format grading checks for each new V198-V203 bank entry.
This is NOT proof of deep mathematical equivalence or novel independent methods.
"""
import sys,sqlite3,json,collections,hashlib,re
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(BASE/'backend'))
from app.ai.engine.service import AIQuestionService
from app.ai.engine.validator import validate
from app.questions.answer_checker import grade_answer
from database.database import DATABASE_PATH
DB=BASE/'backend/database/mathweb.db';assert DB.resolve()==DATABASE_PATH.resolve()
versions=('V198','V199','V200','V201','V202','V203')
expected={'V198':340,'V199':320,'V200':230,'V201':200,'V202':200,'V203':120}
service=AIQuestionService();issues=[];checked=collections.Counter();topics=set()
conn=sqlite3.connect(DB);conn.row_factory=sqlite3.Row
rows=conn.execute("SELECT * FROM admin_question_bank WHERE source IN (?,?,?,?,?,?)",tuple(v+' QA-gated' for v in versions)).fetchall()
assert len(rows)==sum(expected.values()),(len(rows),sum(expected.values()))
for raw in rows:
 d=dict(raw);v=d['source'].split()[0];topics.add((d['grade'],d['topic']));typ=d['question_type'];level={'nền tảng':'easy','trung cấp':'medium','nâng cao':'hard'}[d['difficulty']]
 try:
  d['choices']=json.loads(d['choices_json'] or '[]')
  constructed=service._build_curated_question(d,d['grade'],d['topic'],level,typ)
  assert constructed is not None,'could not build'
  validate(constructed)
  assert bool(grade_answer(constructed,constructed['answer'])),'correct answer rejected'
  if typ=='multiple_choice':
   assert len(constructed['options'])==4
   assert sum(bool(grade_answer(constructed,c)) for c in constructed['options'])==1,'non-unique correct choice'
  elif typ=='true_false':
   assert len(constructed['statements'])==4 and len(constructed['statement_answers'])==4
   assert all(isinstance(x,bool) for x in constructed['statement_answers'])
  else:assert typ=='short_answer'
  checked[v]+=1
 except Exception as e:
  issues.append(dict(bank_id=d['id'],source=v,why=str(e)))
assert {v:checked[v] for v in versions}==expected,issues[:20]
assert not issues
assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
old=sqlite3.connect(BASE/'bank_updates/V198_before_import_backup.sqlite')
ignored=('admin_question_bank','mathweb_bank_import_ledger','mathweb_v198_topic_repair_ledger','sqlite_sequence')
unchanged={}
for (tb,) in old.execute('SELECT name FROM sqlite_master WHERE type="table"'):
 if tb in ignored or tb.startswith('sqlite_'):continue
 try:
  rows_old=old.execute(f'SELECT COUNT(*) FROM "{tb}"').fetchone()[0]
  rows_new=conn.execute(f'SELECT COUNT(*) FROM "{tb}"').fetchone()[0]
  unchanged[tb]={'before':rows_old,'after':rows_new}
 except sqlite3.Error:pass
assert all(x['before']==x['after'] for x in unchanged.values()),unchanged
# normalized full question checks at each grade
seen={};dups=[]
for (rid,g,q) in conn.execute('select id,grade,question from admin_question_bank'):
 norm=re.sub(r'\s+',' ',str(q).strip().casefold())
 key=(g,norm)
 if key in seen:dups.append({'id':rid,'other':seen[key]})
 else:seen[key]=rid
forms=collections.Counter()
for r in rows:
 tags=json.loads(r['tags_json'] or '[]')
 for tag in tags:
  if isinstance(tag,str) and tag.startswith('form:'): forms[(r['source'],tag)]+=1
assert len(forms)==141 and all(n==10 for n in forms.values())
counts={(str(g),t):n for g,t,n in conn.execute('select grade,topic,count(*) from admin_question_bank group by grade,topic')}
index=json.loads((BASE/'backend/app/ai/knowledge/index.json').read_text())
coverage=[{'grade':int(g),'topic':t['id'],'db_question_count':counts.get((g,t['id']),0),'short_of_20000_count_only':max(0,20000-counts.get((g,t['id']),0))} for g,topics in index.items() for t in topics]
assert len(coverage)==150
newdups=[d for d in dups if d['id'] in {r['id'] for r in rows}]
report=dict(version='V203',base='V197 bundled full site',bundled_questions_before=9636,bundled_questions_after=conn.execute('select count(*) from admin_question_bank').fetchone()[0],newly_inserted=sum(expected.values()),v198_to_v203_verified_by_app=dict(checked),candidate_families=len(forms),every_family_has_10=(all(n==10 for n in forms.values())),distinct_topics_extended=len(topics),full_catalog_topics=len(coverage),format_checks_all_new=len(rows)-len(issues),format_failed=issues,normalized_duplicate_questions_in_full_bank=len(dups),normalized_duplicate_questions_among_new=newdups[:100],sqlite_integrity='ok',non_bank_table_counts_unchanged=unchanged,independent_methods_certified=0,production_deployed=False,limits='Exact formula/standalone oracle, validator and grading checks are not mathematical-method independence certification; no live production deployment')
(BASE/'bank_updates/V203_EXHAUSTIVE_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(BASE/'bank_updates/V203_COVERAGE_150.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ('non_bank_table_counts_unchanged','normalized_duplicate_questions_among_new','format_failed')},ensure_ascii=False))
assert not newdups,newdups[:5]
