"""Build additive *candidate* lookup SQLite from user's B56 archive.

Keep the source ZIP untouched (including all Word documents). Never replace V254.
Records are structurally filtered, not independently mathematically certified.
"""
from __future__ import annotations
import hashlib, io, json, re, sqlite3, tempfile, unicodedata, zipfile
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'question_bank_v254_source/Question_Bank_V254_B56_BO_SUNG_CO_KIEM_TRA.zip'
TARGET=ROOT/'backend/app/ai/storage/v254_b56_candidates.seed.zip'
MANIFEST=ROOT/'backend/app/ai/storage/v254_b56_seed_manifest.json'
MAPPING=ROOT/'backend/app/ai/storage/v254_b56_topic_map.json'


def canonical(s):
    s=unicodedata.normalize('NFKC',str(s or '')).casefold()
    s=' '.join(s.split())
    return s

def item_rows(name,raw):
    if name.endswith('.jsonl'):
        for line in raw.decode('utf-8-sig').splitlines():
            if not line.strip():continue
            try: obj=json.loads(line)
            except json.JSONDecodeError: continue
            if isinstance(obj,dict):yield obj
        return
    try: obj=json.loads(raw.decode('utf-8-sig'))
    except (ValueError,UnicodeError):return
    if isinstance(obj,dict) and 'forms' in obj:
        for form in obj.get('forms',[]):
            for row in form.get('questions',[]):
                q=dict(row)
                q.setdefault('source_word',form.get('file'))
                yield q
        return
    if isinstance(obj,dict) and 'questions' in obj:
        for row in obj['questions']:
            if isinstance(row,dict):yield row
        return
    if isinstance(obj,list):
        for item in obj:
            if isinstance(item,dict) and isinstance(item.get('questions'),list):
                for row in item['questions']:
                    if isinstance(row,dict):yield row
            elif isinstance(item,dict):yield item

def files_to_index(names):
    # Only question-bearing structured files, not reports or audit projections.
    return [n for n in names if (
        (n.endswith('.jsonl') and ('QUESTION_RECORDS' in n or n.endswith('RECORDS.jsonl') or 'NGAN_HANG' in n))
        or n.endswith('QUESTION_RECORDS_B21.json')
        or n in ('V254_B55/BO_SUNG_10_CAU.json','V254_B56/BO_SUNG_20_CAU.json',
                 'NGAN_HANG_001_440_CAU_MOI.json','NGAN_HANG_B03_100_CAU.json',
                 'B04_003_010_NOI_DUNG.json')
    )]

def infer_number(item,name):
    raw=item.get('topic_id') or item.get('topic')
    if isinstance(raw,int) or (isinstance(raw,str) and raw.strip().isdigit()): return int(raw)
    for field in ('source_word','word','path','file'):
        match=re.search(r'(?:^|/)(\d{3})_Toan_',str(item.get(field,'')))
        if match:return int(match.group(1))
    # Scoped files B55 and B56 give explicit topic indexes in record IDs.
    match=re.search(r'[-_](\d{3})[-_]',str(item.get('id','')))
    if match: return int(match.group(1))
    if 'NGAN_HANG_001' in name:return 1
    return None

def main():
    mapping=json.loads(MAPPING.read_text(encoding='utf-8'))
    counts=Counter(); bytopic=Counter(); seen=set()
    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/'v254_b56_candidates.sqlite'
        con=sqlite3.connect(str(db))
        con.execute('PRAGMA journal_mode=DELETE')
        con.execute('CREATE TABLE questions (id TEXT PRIMARY KEY, grade INTEGER NOT NULL, topic TEXT NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL, solution TEXT NOT NULL, options TEXT NOT NULL, question_type TEXT NOT NULL, difficulty TEXT NOT NULL, source TEXT NOT NULL)')
        with zipfile.ZipFile(SOURCE) as bank:
            for n in files_to_index(bank.namelist()):
                for item in item_rows(n,bank.read(n)):
                    counts['source_rows']+=1
                    num=infer_number(item,n); info=mapping.get(str(num))
                    if not info:
                        counts['unmapped']+=1;continue
                    q=str(item.get('question') or item.get('stem') or item.get('problem') or '').strip()
                    a=str(item.get('answer') or item.get('symbolic_answer') or '').strip()
                    sol=str(item.get('solution') or item.get('explanation') or '').strip()
                    if not (8<=len(q)<=1800 and 1<=len(a)<=250 and 12<=len(sol)<=2800):
                        counts['incomplete']+=1;continue
                    norm=canonical(q)
                    if norm in seen:
                        counts['duplicate_exact']+=1;continue
                    seen.add(norm)
                    opts=item.get('options') or item.get('choices') or []
                    if isinstance(opts,str):
                        try:opts=json.loads(opts)
                        except ValueError:opts=[]
                    # A multiple-choice candidate is usable only with valid choices and one correct answer.
                    if isinstance(opts,list) and len(opts)==4 and len({canonical(x) for x in opts})==4 and a in [str(x).strip() for x in opts]:
                        qtype='multiple_choice'
                    else:
                        opts=[];qtype='short_answer'
                    lvl=canonical(item.get('level') or item.get('difficulty') or 'medium')
                    diff='easy' if lvl in ('nen tang','nền tảng','foundation','easy') else 'hard' if lvl in ('nang cao','nâng cao','hard','expert') else 'medium'
                    ident='b56:'+str(item.get('id') or hashlib.sha256((str(num)+':'+norm).encode()).hexdigest()[:22])
                    try:
                        con.execute('INSERT INTO questions VALUES(?,?,?,?,?,?,?,?,?,?)', (ident,info['grade'],info['topic'],q,a,sol,json.dumps(opts,ensure_ascii=False),qtype,diff,n))
                        counts['indexed']+=1;bytopic[f"{info['grade']}:{info['topic']}"]+=1
                    except sqlite3.IntegrityError: counts['id_collision']+=1
        con.execute('CREATE INDEX idx_b56_pick ON questions(grade,topic,difficulty,question_type)')
        con.commit(); con.close()
        data=db.read_bytes()
    TARGET.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('v254_b56_candidates.sqlite',data)
    manifest={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_archive':SOURCE.name,'status':'candidate_not_independently_certified','counts':dict(counts),'covered_grade_topics':len(bytopic),'by_topic':dict(bytopic),'original_word_files':150}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='by_topic'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
