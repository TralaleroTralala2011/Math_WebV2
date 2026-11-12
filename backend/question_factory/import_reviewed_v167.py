"""Conservative, idempotent importer for independently checked numerical questions.

Never certifies mathematical method independence. Never touches account databases.
Use --db to point to a SEPARATE Question Factory SQLite database.
"""
import argparse, hashlib, json, re, time, zipfile
from pathlib import Path
from . import storage

SOURCES={'v162_quadratic_sequence_sum','v166_arithmetic_sum'}

def verified_value(row):
    p=row['parameters']; m=row['method_id']
    if m=='v166_arithmetic_sum':
        u,d,n=(int(p[k]) for k in ('u1','d','n'))
        assert 1<=n<=1000
        value=sum(u+i*d for i in range(n))
    elif m=='v162_quadratic_sequence_sum':
        a,b,c,n=(int(p[k]) for k in ('a','b','c','n'))
        assert 1<=n<=1000
        value=sum(a*k*k+b*k+c for k in range(1,n+1))
    else: raise ValueError('unsupported method')
    if str(value)!=str(row['answer']).strip() or str(value)!=str(row['canonical_answer']).strip():
        raise ValueError('independent oracle mismatch: '+row['id'])
    if not row.get('solution') or str(value) not in row['solution']:
        raise ValueError('solution lacks computed result: '+row['id'])
    return value

def import_rows(db, source_zip):
    storage.initialize(db)
    imported=0; reused=0; rejected=[]
    with zipfile.ZipFile(source_zip) as z:
        rows=[]
        for name in z.namelist():
            if name.endswith('_PENDING_QUESTIONS.jsonl'):
                rows += [json.loads(line) for line in z.read(name).splitlines() if line.strip()]
    with storage.connect(db) as con:
        for row in rows:
            if row.get('method_id') not in SOURCES: continue
            try:
                verified_value(row)
                if row.get('format')!='tu_luan' or row.get('grade')!=11: raise ValueError('unexpected format/grade')
                if not re.fullmatch(r'[a-z0-9_]+',row['id']): raise ValueError('bad id')
                topic=row['topic']; method=row['method_id']
                if not con.execute('SELECT 1 FROM topics WHERE id=? AND grade=11',(topic,)).fetchone():
                    raise ValueError('topic missing: '+topic)
                fingerprint=hashlib.sha256(row['question'].strip().encode()).hexdigest()
                with storage.transaction(con):
                    existing=con.execute('SELECT id,stem,answer FROM questions WHERE id=?',(row['id'],)).fetchone()
                    if existing:
                        if existing['stem']!=row['question'] or existing['answer']!=str(row['answer']):
                            raise ValueError('ID collision')
                        reused+=1;continue
                    a=con.execute('SELECT id FROM archetypes WHERE id=?',(method,)).fetchone()
                    if not a:
                        con.execute('''INSERT INTO archetypes(id,topic_id,family,name,method_signature,difficulty,review_status,reviewer,reviewed_at)
                         VALUES(?,?,?,?,?,?,?,?,?)''',(method,topic,method,'Independently checked numerical exercise: '+method,
                          method,'trung cấp','approved','automated-numeric-oracle',time.time()))
                    ordinal=int(row['id'].rsplit('_',1)[1])+1
                    con.execute('''INSERT INTO questions(id,archetype_id,ordinal,fingerprint,stem,answer,solution,params_json,difficulty,validation_json,status,verified_at)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',(row['id'],method,ordinal,fingerprint,row['question'],str(row['answer']),row['solution'],json.dumps(row['parameters'],ensure_ascii=False),'trung cấp',json.dumps({'oracle':'independent-direct-sum','method_independence_certified':False}),'verified',time.time()))
                    imported+=1
            except Exception as e:
                rejected.append({'id':row.get('id'),'reason':str(e)})
    return {'imported':imported,'already_present':reused,'rejected':rejected,'method_independence_certified':0}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--db',required=True);ap.add_argument('--source-zip',required=True);args=ap.parse_args()
    print(json.dumps(import_rows(args.db,args.source_zip),ensure_ascii=False,indent=2))
