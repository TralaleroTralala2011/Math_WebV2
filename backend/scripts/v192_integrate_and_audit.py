#!/usr/bin/env python3
"""V192 deterministic staging merge, full catalog report, and QA-gated local DB rehearsal.
No remote/live production write. The caller may import into an isolated copy of V191's SQLite.
"""
from __future__ import annotations
import sys,csv,json,re,sqlite3,hashlib,collections,tempfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BANK=ROOT/'bank_updates'
sys.path.insert(0,str(ROOT/'backend'))
from scripts.import_bank_updates import load_and_validate
from app.questions.answer_checker import grade_answer
from app.ai.engine import service

def sha(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def canon(s): return ' '.join(str(s).casefold().split())

def run():
 old=list(map(json.loads,(BANK/'V191_CUMULATIVE_QA_IMPORT.jsonl').read_text(encoding='utf8').splitlines()))
 new=list(map(json.loads,(BANK/'V192_IMPORT_READY.jsonl').read_text(encoding='utf8').splitlines()))
 assert len(old)==7636 and len(new)==1500
 seen_ids=set();seen_questions=set();combined=[];rejected=[]
 for r in old+new:
  rid=r['id'];key=(int(r['grade']),canon(r['question']))
  if rid in seen_ids or key in seen_questions:
   rejected.append(rid);continue
  seen_ids.add(rid);seen_questions.add(key);combined.append(r)
 assert len(combined)==9136 and not rejected
 with (BANK/'V192_CUMULATIVE_QA_IMPORT.jsonl').open('w',encoding='utf8') as f:
  for row in combined:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 checked=load_and_validate(BANK/'V192_CUMULATIVE_QA_IMPORT.jsonl')
 assert len(checked)==9136
 assert all(x['answer'] and x['solution'] and x['question'] for x in checked)
 catalog=json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text(encoding='utf8'))
 names={(int(g),r['id']):r['name'] for g,arr in catalog.items() for r in arr}
 assert len(names)==150
 count=collections.Counter((int(r['grade']),r['topic']) for r in combined)
 newct=collections.Counter((int(r['grade']),r['topic']) for r in new)
 forms=collections.Counter((r['grade'],r['topic'],r['form_id']) for r in new)
 assert len(forms)==150 and all(v==10 for v in forms.values())
 assert len(newct)==150 and all(v==10 for v in newct.values())
 per=[]
 for (g,t),name in names.items():
  per.append({'grade':g,'topic':t,'topic_name':name,
              'qa_staging_previous_v191':count[g,t]-newct[g,t],
              'v192_new_oracle_checked_questions':newct[g,t],
              'staged_qa_total':count[g,t],
              'v192_candidate_families':len([f for f in forms if f[0]==g and f[1]==t]),
              'certified_independent_families':0,
              'live_production_question_count':None,
              'missing_independent_families_in_production':None,
              'missing_verified_questions_in_production':None,
              'target_independent_families':2000,
              'target_questions':20000})
 assert len(per)==150
 with (BANK/'V192_COVERAGE_150_STAGING.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(per[0]));w.writeheader();w.writerows(per)
 (BANK/'V192_COVERAGE_150_STAGING.json').write_text(json.dumps({
  'scope':'V192 local SQLite bank (NOT remote production); no independent-type certification',
  'topic_count':len(per),'total_qa_rows':len(checked),'new_rows':len(new),'per_topic':per
 },ensure_ascii=False,indent=2)+'\n',encoding='utf8')

 # Local package database is based on V191 with pre-existing account data, so never delete it.
 db=ROOT/'backend/database/mathweb.db'
 assert db.exists()
 with sqlite3.connect(db) as c:
  tables=c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
  assert ('users',) in tables and ('admin_question_bank',) in tables
  user_before=c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
  oldbank=c.execute('SELECT COUNT(*) FROM admin_question_bank').fetchone()[0]
  nonbank_snap={}
  for t in ('users','game_results','friends','messages','notifications','question_sessions'):
   arr=c.execute(f'SELECT * FROM {t}').fetchall()
   nonbank_snap[t]=(len(arr),sha(repr(arr)))
  assert oldbank==0, ('Unexpected source bank rows; script intentionally refuses overwrite',oldbank)

 cmd=[sys.executable,str(ROOT/'backend/scripts/import_bank_updates.py'),
  '--db',str(db),'--input',str(BANK/'V192_CUMULATIVE_QA_IMPORT.jsonl')]
 preview=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=240)
 p=json.loads(preview.stdout)
 assert p['potential_new']==len(combined) and p['bank_before']==0
 backup=ROOT.parent/'V191_SQLITE_ORIGINAL_BACKUP_RECHECK.sqlite'
 if backup.exists():raise RuntimeError('Refusing to overwrite backup')
 first=subprocess.run(cmd+['--write','--backup',str(backup)],capture_output=True,text=True,check=True,timeout=240)
 w=json.loads(first.stdout)
 assert w['inserted']==len(combined) and w['bank_after']==len(combined)
 backup2=ROOT.parent/'V192_SQLITE_SECOND_IMPORT_BACKUP_RECHECK.sqlite'
 if backup2.exists():raise RuntimeError('Refusing to overwrite second backup')
 second=subprocess.run(cmd+['--write','--backup',str(backup2)],capture_output=True,text=True,check=True,timeout=240)
 w2=json.loads(second.stdout)
 assert w2['inserted']==0 and w2['already_present']==len(combined)

 with sqlite3.connect(db) as c:
  assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  for t,(n,d) in nonbank_snap.items():
   arr=c.execute(f'SELECT * FROM {t}').fetchall()
   assert (len(arr),sha(repr(arr)))==(n,d),('nonbank table changed',t)
  assert c.execute('SELECT COUNT(*) FROM users').fetchone()[0]==user_before
  imported_ids={r['id'] for r in new}
  sample_bank_ids=c.execute('SELECT count(*) FROM mathweb_bank_import_ledger WHERE source_id LIKE "v192_%"').fetchone()[0]
  assert sample_bank_ids==len(new)
  tagged_rows=c.execute('SELECT count(*) FROM admin_question_bank WHERE source LIKE "V192%"').fetchone()[0]
  assert tagged_rows==len(new)

 # The application service fetches actual questions from this SQLite database.
 old_conn=service.get_connection
 def get_c():
  con=sqlite3.connect(db);con.row_factory=sqlite3.Row;return con
 service.get_connection=get_c
 samples=[]
 try:
  ai=service.AIQuestionService()
  selected=[(10,'menh_de'),(11,'ham_so_luong_giac'),(12,'g12_geom_sphere_plane_intersection')]
  for g,t in selected:
   for fmt in ('multiple_choice','short_answer','true_false'):
    cands=ai._curated_admin_candidates(g,t,'medium',fmt)
    if not cands:cands=ai._curated_admin_candidates(g,t,'easy',fmt)
    assert cands,(g,t,fmt)
    # Prefer newly added V192 entry to ensure routing to new bank rows.
    preferred=[q for q in cands if 'V192' in str(q)]
    c=preferred[0] if preferred else cands[0]
    built=ai._build_curated_question(c,g,t,'medium',fmt)
    assert built and grade_answer(built,built['answer']), (g,t,fmt)
    if fmt=='multiple_choice':assert sum(bool(grade_answer(built,o)) for o in built['options'])==1
    samples.append({'grade':g,'topic':t,'question_type':fmt,'success':True})
 finally:
  service.get_connection=old_conn

 report={'version':'MATH_WEB_GITHUB_READY_V192','base':'MATH_WEB_GITHUB_READY_V191_FULL_WEB_BANK_QA_IMPORT.zip',
  'catalog_checked':150,'new_candidate_family_count':len(forms),
  'new_questions_exact_math_and_grader_checked':len(new),
  'new_questions_by_grade':dict(collections.Counter(str(r['grade']) for r in new)),
  'new_question_types':dict(collections.Counter(r['question_type'] for r in new)),
  'new_topics_expanded':len(newct),'qa_staging_total':len(combined),
  'new_independent_family_certifications':0,'remote_production_new_questions_confirmed':0,
  'web_bundle_sqlite_before':oldbank,'web_bundle_sqlite_imported':w['inserted'],
  'web_bundle_sqlite_after':w['bank_after'],'web_bundle_sqlite_second_import_added':w2['inserted'],
  'new_V192_rows_in_bundle_sqlite':tagged_rows,
  'nonbank_tables_verified_unchanged':list(nonbank_snap),
  'web_bundle_application_retrieval_grade_samples':samples,
  'web_bundle_sqlite_integrity':'ok','source_db_backup_outside_zip':str(backup),
  'global_semantic_dedup':'not certified; exact and numeric-template overlap tests only',
  'missing_per_topic_production':'unknown; production SQLite inaccessible',
  'target_new_families_per_session':10000,'target_new_questions_per_session':100000,
  'target_final_families':300000,'target_final_questions':3000000,
  'note':'Bundled copy of active MATH_WEB SQLite was populated. No remote production database was accessed.'}
 (BANK/'V192_RELEASE_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (BANK/'V192_IMPORT_REHEARSAL.json').write_text(json.dumps({'preview':p,'first_import':w,'second_import':w2,'retrieval_samples':samples,'nonbank_invariants':nonbank_snap,'production_write':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k in ('catalog_checked','new_candidate_family_count','new_questions_exact_math_and_grader_checked','qa_staging_total','web_bundle_sqlite_imported','web_bundle_sqlite_after','web_bundle_sqlite_second_import_added','new_V192_rows_in_bundle_sqlite','new_independent_family_certifications','remote_production_new_questions_confirmed')},ensure_ascii=False))

if __name__=='__main__':run()
