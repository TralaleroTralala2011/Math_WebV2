"""Restore the versioned READ-ONLY question bank from a tracked ZIP before Render starts.

Never overwrite a pre-existing valid database. It is bundled reference data,
NOT the separate mutable users database. No network or external modules needed.
"""
from pathlib import Path
import hashlib,json,os,sqlite3,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend'/'app'/'ai'/'storage'
DB=BASE/'v254_candidates.sqlite'
SEED=BASE/'v254_candidates.seed.zip'
MANIFEST=BASE/'v254_seed_manifest.json'

def valid(path, expected):
    if not path.is_file() or path.stat().st_size != expected['bytes']:
        return False
    sha=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):sha.update(chunk)
    if sha.hexdigest()!=expected['sha256']:
        return False
    with sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True) as db:
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':return False
        for table in ('questions','b54_word_labels'):
            if db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]!=expected[table]:return False
    return True

def main():
    expected=json.loads(MANIFEST.read_text(encoding='utf-8'))
    if valid(DB,expected):
        print('V254/B54 bank ready, records:',expected['questions'],expected['b54_word_labels'])
        return 0
    if not SEED.is_file():
        print('ERROR: missing packaged bank archive:',SEED,file=sys.stderr);return 2
    with zipfile.ZipFile(SEED) as z:
        if z.namelist()!=['v254_candidates.sqlite']:
            raise RuntimeError('Unexpected archive member list')
        tmp=DB.with_suffix('.sqlite.restoring')
        try:
            with z.open('v254_candidates.sqlite') as i, tmp.open('wb') as o:
                for chunk in iter(lambda:i.read(1024*1024),b''):o.write(chunk)
            if not valid(tmp,expected):raise RuntimeError('Bank hash, schema or counts mismatch')
            os.replace(tmp,DB)
        finally:
            tmp.unlink(missing_ok=True)
    print('Restored V254/B54 bank:',DB)
    return 0

if __name__=='__main__':raise SystemExit(main())
