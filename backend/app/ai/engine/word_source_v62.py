"""Source-faithful, indexed read-only bank extracted from 150 supplied Word files.

No answers are exposed by public availability endpoints. `questions` are candidates:
source format and internal deduplication checked, not independent math-proofed.
"""
from __future__ import annotations

import functools
import hashlib
import json
import os
import sqlite3
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path

STORAGE = Path(__file__).resolve().parents[1] / 'storage'
DB_FILE = STORAGE / 'v62_word_source.sqlite'
SEED_FILE = STORAGE / 'v62_word_source.seed.zip'
MANIFEST = STORAGE / 'v62_word_source_manifest.json'


def _digest(path:Path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda:handle.read(2**20),b''):
            h.update(block)
    return h.hexdigest()


def _verified(path, manifest):
    try:
        if not path.is_file() or path.stat().st_size != manifest['db_bytes']:
            return False
        if _digest(path) != manifest['db_sha256']:
            return False
        with closing(sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True)) as conn:
            return conn.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
    except (OSError,sqlite3.Error,KeyError):
        return False


@functools.lru_cache(maxsize=1)
def ensure_word_source():
    """Use bundled SQLite first; recover seed when missing without touching user DB."""
    try:
        manifest=json.loads(MANIFEST.read_text(encoding='utf8'))
    except (OSError,ValueError):
        return None
    if _verified(DB_FILE,manifest):
        return DB_FILE
    if not SEED_FILE.is_file():
        return None
    # A cloud filesystem may be immutable. Use a separate temporary cache.
    cache_dir = Path(os.environ.get('MATHWEB_WORD_SOURCE_CACHE') or tempfile.gettempdir())
    try:
        cache_dir.mkdir(parents=True,exist_ok=True)
        target = cache_dir / ('mathweb_word62_' + manifest['db_sha256'][:18] + '.sqlite')
        if _verified(target,manifest):
            return target
        with zipfile.ZipFile(SEED_FILE) as z:
            if z.namelist() != ['v62_word_source.sqlite']:
                return None
            with z.open('v62_word_source.sqlite') as inp, tempfile.NamedTemporaryFile(prefix='.word62_',suffix='.db',dir=cache_dir,delete=False) as out:
                temporary = Path(out.name)
                try:
                    for block in iter(lambda: inp.read(2**20),b''):
                        out.write(block)
                except BaseException:
                    temporary.unlink(missing_ok=True)
                    raise
        if not _verified(temporary,manifest):
            temporary.unlink(missing_ok=True)
            return None
        os.replace(temporary,target)
        return target
    except (OSError,ValueError,KeyError,sqlite3.Error,zipfile.BadZipFile):
        return None


def select_word_questions(grade:int,topic:str,difficulty:str,question_type:str,limit:int=100):
    """Fetch only exact grade/topic/difficulty/type using indexed SQL."""
    path=ensure_word_source()
    if path is None or question_type not in ('short_answer','multiple_choice'):
        return []
    if not topic or len(str(topic)) > 150 or grade not in (10,11,12):
        return []
    try:
        with closing(sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True,timeout=3)) as conn:
            conn.row_factory=sqlite3.Row
            data=conn.execute(
                '''SELECT id,question,answer,solution,options,question_type,difficulty,source,
                          source_word,source_question_number,status,form_id,form_title
                   FROM questions WHERE grade=? AND topic=? AND difficulty=? AND question_type=?
                   ORDER BY RANDOM() LIMIT ?''',
                (int(grade),str(topic),str(difficulty),question_type,max(1,min(150,int(limit))))
            ).fetchall()
            return [dict(r) for r in data]
    except (OSError,ValueError,sqlite3.Error):
        return []


def source_availability(grade:int|None=None, topic:str|None=None):
    """Return counts and source metadata only; never leak correct answers."""
    path=ensure_word_source()
    if path is None:
        return {'available':False,'reason':'word_source_bank_missing_or_invalid'}
    manifest=json.loads(MANIFEST.read_text(encoding='utf8'))
    query = ('SELECT grade,topic,question_type,difficulty,COUNT(*) AS total FROM questions WHERE 1=1')
    params=[]
    if grade is not None:
        query+=' AND grade=?';params.append(int(grade))
    if topic:
        query+=' AND topic=?';params.append(str(topic))
    query+=' GROUP BY grade,topic,question_type,difficulty ORDER BY grade,topic,question_type,difficulty'
    with closing(sqlite3.connect(f'file:{path.as_posix()}?mode=ro',uri=True)) as conn:
        rows=[dict(zip(('grade','topic','question_type','difficulty','count'),row)) for row in conn.execute(query,params)]
    return {'available':True,'source_word_files':manifest['source_files'],
            'source_sha256':manifest['source_sha256'],
            'quality_status':'candidate_unverified',
            'matched_question_count':sum(row['count'] for row in rows),
            'topics':rows}
