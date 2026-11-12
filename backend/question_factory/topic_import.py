"""Import an authoritative grade 10..12 topic catalog; never fabricate missing topics."""
import json
import re
from pathlib import Path
from contextlib import closing
from .storage import connect, transaction


def import_topics(db_path, json_path, expected_count=150):
    data=json.loads(Path(json_path).read_text(encoding='utf-8'))
    if not isinstance(data,list) or len(data)!=expected_count:
        raise ValueError(f'expected {expected_count} topic records, found '+str(len(data) if isinstance(data,list) else 'non-array'))
    ids=set()
    for topic in data:
        if not isinstance(topic,dict) or set(topic)!={'id','grade','name'}:
            raise ValueError('each topic must contain only id, grade, name')
        if not isinstance(topic['grade'],int) or topic['grade'] not in (10,11,12):
            raise ValueError('grade must be 10, 11 or 12')
        if (not isinstance(topic['id'],str) or
            not re.fullmatch(r'[a-z0-9]+(?:[-_][a-z0-9]+)*',topic['id']) or
            not isinstance(topic['name'],str) or not topic['name'].strip()):
            raise ValueError('invalid topic id/name')
        if topic['id'] in ids:
            raise ValueError('duplicate topic id: '+topic['id'])
        ids.add(topic['id'])
    with closing(connect(db_path)) as con, transaction(con):
        # Explicit mismatch prevents the import from silently renaming existing topics.
        for topic in data:
            old=con.execute('SELECT grade,name FROM topics WHERE id=?',(topic['id'],)).fetchone()
            if old and (old['grade']!=topic['grade'] or old['name']!=topic['name']):
                raise ValueError('catalog conflict with existing topic: '+topic['id'])
            con.execute('INSERT OR IGNORE INTO topics(id,grade,name) VALUES(?,?,?)',
                        (topic['id'],topic['grade'],topic['name']))
    return len(data)
