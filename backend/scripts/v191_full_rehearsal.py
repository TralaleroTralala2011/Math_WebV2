#!/usr/bin/env python3
"""Offline rehearsal of cumulative bank import, not a production migration.
Creates an isolated temporary SQLite bank, verifies read/grade and re-import no-ops.
"""
from pathlib import Path
import sys,json,tempfile,subprocess,sqlite3,collections
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'bank_updates/V191_CUMULATIVE_QA_IMPORT.jsonl'
REPORT=ROOT/'bank_updates/V191_IMPORT_REHEARSAL.json'
sys.path.insert(0,str(ROOT/'backend'))
from scripts.import_bank_updates import load_and_validate
from app.questions.answer_checker import grade_answer
from app.ai.engine import service

def run():
 rows=load_and_validate(DATA)
 assert rows
 with tempfile.TemporaryDirectory(prefix='mathweb_v191_import_test_') as folder:
  path=Path(folder)/'mathweb-fixture.sqlite'
  conn=sqlite3.connect(path)
  conn.executescript('''CREATE TABLE admin_question_bank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade INTEGER NOT NULL, topic TEXT NOT NULL, difficulty TEXT NOT NULL,
    question_type TEXT NOT NULL, game_id TEXT NOT NULL DEFAULT '',
    question TEXT NOT NULL, choices_json TEXT NOT NULL DEFAULT '[]',
    correct_answer TEXT NOT NULL, explanation TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'Admin MATH_WEB', tags_json TEXT NOT NULL DEFAULT '[]',
    created_by INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE INDEX idx_admin_questions_topic ON admin_question_bank(grade,topic,difficulty);
    ''')
  conn.commit();conn.close()
  script=ROOT/'backend/scripts/import_bank_updates.py'
  cmd=[sys.executable,str(script),'--db',str(path),'--input',str(DATA)]
  preview=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=True)
  write1=subprocess.run(cmd+['--write','--backup',str(Path(folder)/'backup1.sqlite')],capture_output=True,text=True,timeout=180)
  if write1.returncode:raise RuntimeError(write1.stderr)
  w1=json.loads(write1.stdout)
  assert w1['inserted']==len(rows)==w1['bank_after']
  write2=subprocess.run(cmd+['--write','--backup',str(Path(folder)/'backup2.sqlite')],capture_output=True,text=True,timeout=180,check=True)
  w2=json.loads(write2.stdout)
  assert w2['inserted']==0 and w2['already_present']==len(rows) and w2['bank_after']==len(rows)
  # Entire saved bank can be retrieved and graded via the application-specific adapter.
  old=service.get_connection
  def connect_fixture():
   c=sqlite3.connect(path);c.row_factory=sqlite3.Row;return c
  service.get_connection=connect_fixture
  samples=[]
  try:
   api=service.AIQuestionService()
   for g,t in [(10,'tap_hop'),(11,'cap_so_nhan'),(12,'g12_geom_sphere_equation')]:
    for fmt in ('multiple_choice','short_answer','true_false'):
     cands=api._curated_admin_candidates(g,t,'medium',fmt)
     if not cands and (g,t)==(10,'tap_hop'):
      cands=api._curated_admin_candidates(g,t,'easy',fmt)
     assert cands,(g,t,fmt)
     out=api._build_curated_question(cands[0],g,t,'medium',fmt)
     assert out and grade_answer(out,out['answer'])
     if fmt=='multiple_choice':
      assert sum(grade_answer(out,option) for option in out['options'])==1
     samples.append({'grade':g,'topic':t,'type':fmt,'pass':True})
  finally:
   service.get_connection=old
  report={'phase':'sandbox_offline_not_production','input_rows':len(rows),
          'source_bundles':dict(collections.Counter(r.get('source_bundle','unknown') for r in rows)),
          'sqlite_preview':json.loads(preview.stdout),
          'first_write':{k:w1[k] for k in ('bank_before','inserted','bank_after','ledger_confirmed','sqlite_integrity')},
          'second_write':{k:w2[k] for k in ('bank_before','inserted','already_present','bank_after','ledger_confirmed','sqlite_integrity')},
          'retrieval_grading_checks':samples,'production_confirmed_inserted':0,
          'independent_types_certified':0}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k not in ('sqlite_preview','retrieval_grading_checks','source_bundles')},ensure_ascii=False))
if __name__=='__main__':run()
