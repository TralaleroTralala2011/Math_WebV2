"""Run backend pytest with all default SQLite files redirected to disposable storage.

This protects the shipped legacy users/XP databases from tests that initialize
real FastAPI routes and would otherwise create test accounts in backend/database.

Example: python scripts/run_tests_isolated.py -q tests/test_api_integration.py
"""
from pathlib import Path
import hashlib
import os
import subprocess
import sys
import tempfile

BACKEND=Path(__file__).resolve().parents[1]
DB_SUFFIXES={'.db','.sqlite','.sqlite3'}


def inventory():
    # Protect every SQLite file in the project, including older nested copies.
    return {str(p.relative_to(BACKEND.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in BACKEND.parent.rglob('*')
            if p.is_file() and p.suffix in DB_SUFFIXES and '.venv' not in p.parts}


def main(argv=None):
    args=list(sys.argv[1:] if argv is None else argv)
    before=inventory()
    with tempfile.TemporaryDirectory(prefix='mathweb-isolated-tests-') as t:
        data=Path(t)/'data'
        data.mkdir()
        env=os.environ.copy()
        env.update({
            'MATHWEB_DATA_DIR':str(data),
            'MATHWEB_DB_PATH':str(data/'mathweb.db'),
            'MATHWEB_AI_HISTORY_DB_PATH':str(data/'mathweb_ai_history.sqlite3'),
            'QF_DB_PATH':str(data/'question_factory.sqlite3'),
            'PYTHONPATH':str(BACKEND)+os.pathsep+env.get('PYTHONPATH',''),
        })
        result=subprocess.run([sys.executable,'-m','pytest',*args],cwd=BACKEND,env=env,check=False)
    after=inventory()
    if before!=after:
        changed=sorted(set(before)|set(after))
        changed=[name for name in changed if before.get(name)!=after.get(name)]
        print('UNEXPECTED PROJECT DATABASE MODIFICATION:',changed,file=sys.stderr)
        return 3
    print('PASS: pre-existing SQLite files remained byte-for-byte unchanged')
    return result.returncode


if __name__=='__main__':
    raise SystemExit(main())
