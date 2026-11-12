"""Run backend pytest against isolated scratch databases, never the shipped data.

Usage from the MATH_WEB_GITHUB_READY root:
  python scripts/run_backend_tests_isolated.py -q tests
Defaults to -q tests when no pytest arguments are supplied.
Requires pytest to be available in the current Python environment.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
BACKEND=ROOT/'backend'
DATABASES=BACKEND/'database'

def digest(path):
 return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def main(argv=None):
 db=DATABASES/'mathweb.db'
 ai=DATABASES/'mathweb_ai_history.sqlite3'
 before={str(p):digest(p) for p in (db,ai)}
 with tempfile.TemporaryDirectory(prefix='mathweb_test_isolated_') as tmp:
  tmpdir=Path(tmp)
  for p,target in ((db,'test_main.db'),(ai,'test_history.db')):
   if p.is_file():shutil.copy2(p,tmpdir/target)
  env=os.environ.copy()
  env['MATHWEB_DB_PATH']=str(tmpdir/'test_main.db')
  env['MATHWEB_AI_HISTORY_DB_PATH']=str(tmpdir/'test_history.db')
  env['PYTHONPATH']=str(BACKEND)+os.pathsep+env.get('PYTHONPATH','')
  args=argv if argv is not None else sys.argv[1:]
  args=args or ['-q','tests']
  completed=subprocess.run([sys.executable,'-m','pytest',*args],cwd=BACKEND,env=env,check=False)
 after={str(p):digest(p) for p in (db,ai)}
 unchanged=before==after
 print('Packaged database checksums unchanged:',unchanged,flush=True)
 if not unchanged:
  for p in before:
   if before[p]!=after[p]:print('WARNING: packaged database changed during tests:',p,flush=True)
 return completed.returncode if unchanged else 2

if __name__=='__main__':raise SystemExit(main())
