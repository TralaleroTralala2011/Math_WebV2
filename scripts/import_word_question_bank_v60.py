#!/usr/bin/env python3
"""Import a bundled Word question-bank *as reviewable candidate data*.

Never edits user databases, original Word documents, or V254/B56/V59 databases.
Exports one JSONL per Word topic; creates a read-only, duplicate-screened overlay.
Run: python scripts/import_word_question_bank_v60.py --source /path/to/150_CHU_DE_WORD.zip
"""
from __future__ import annotations
import argparse, collections, hashlib, io, json, re, sqlite3, unicodedata, zipfile
from pathlib import Path
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
STORAGE=ROOT/'backend/app/ai/storage'
TOPIC_MAP=STORAGE/'v254_b56_topic_map.json'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
QUESTION=re.compile(r'^Câu\s*(?:hỏi\s*)?(?:số\s*)?0*(\d+)\b\s*[.:·\-]?\s*(.*)$', re.I)
DE=re.compile(r'^Đề\s*bài\s*[:：]\s*',re.I)
ANS=re.compile(r'^Đáp\s*án\s*(?:\([^)]*\))?\s*[:：]\s*',re.I)
SOL=re.compile(r'^Lời\s*giải(?:\s+chi\s+tiết)?\s*[:：]\s*',re.I)
OPTS=re.compile(r'(?<![\w])([A-D])\s*[.)]\s*')
NEWLINE_RE=re.compile(r'\s+')


def canonical(s):
    s=unicodedata.normalize('NFKC',str(s or '')).replace('\u200b','').replace('−','-').replace('–','-')
    s=re.sub(r'\s*([=+*/;(),?:])\s*', r'\1',s)
    return ' '.join(s.casefold().split()).strip(' .')


def sha_prompt(s):return hashlib.sha256(canonical(s).encode('utf8')).hexdigest()


def paragraphs(docx_bytes):
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as doc:
        root=etree.fromstring(doc.read('word/document.xml'))
        for para in root.iter(W+'p'):
            val=''.join(t.text or '' for t in para.iter(W+'t')).strip()
            if not val:continue
            style=para.find(W+'pPr/'+W+'pStyle')
            yield style.get(W+'val','') if style is not None else '',val


def split_options(text):
    matches=list(OPTS.finditer(text))
    if len(matches)<4:return text,[]
    # Last four A/B/C/D markers in order; accept inline MCQ only when unambiguous.
    for start in range(len(matches)-3):
        subset=matches[start:start+4]
        if [m.group(1).upper() for m in subset] != list('ABCD'): continue
        if start+4 < len(matches):continue
        stem=text[:subset[0].start()].strip()
        opts=[text[m.end():subset[i+1].start() if i<3 else len(text)].strip(' \t\n;') for i,m in enumerate(subset)]
        if stem and all(opts) and all(len(x)<180 for x in opts):
            return stem,opts
    return text,[]


def normalize_answer(raw,options):
    raw=str(raw or '').strip()
    if len(options)==4:
        m=re.match(r'^([A-D])\b(?:\s*[.)-]|\s|$)',raw,re.I)
        if m:return options[ord(m.group(1).upper())-ord('A')], 'multiple_choice'
        if raw in options:return raw, 'multiple_choice'
        # An answer written 'C (123)' has already been covered above.
        return raw,'unusable_mcq'
    if re.match(r'^[A-D]\b\s*[.):\-]',raw,re.I):return raw,'unusable_mcq'
    # For binary assertions, keep only the expected verdict; the numerical
    # correction belongs in the solution, not in the answer checker.
    if re.match(r'^(đúng|sai)\s*;',raw,re.I):
        raw=re.split(r'\s*;',raw,maxsplit=1)[0].strip()
    return raw,'short_answer'


def get_existing_signatures():
    seen=set()
    for name in ('v254_candidates.sqlite','v59_screened_additions.sqlite'):
        file=STORAGE/name
        if not file.exists():continue
        with sqlite3.connect(f'file:{file.as_posix()}?mode=ro',uri=True) as db:
            for (txt,) in db.execute('SELECT question FROM questions'):
                if txt:seen.add(sha_prompt(txt))
    return seen


def enumerate_items(paras):
    current=None
    for style,s in paras:
        match=QUESTION.match(s)
        if match:
            if current:yield current
            suffix=match.group(2).strip()
            if re.match(r'^(?:tự\s*luận|trả\s*lời\s*ngắn|trắc\s*nghiệm|đúng\s*sai)\b',suffix,re.I):suffix=''
            current={'number':int(match.group(1)),'stem':suffix,'answer':'','solution':'','form':'','difficulty':'medium'}
            continue
        if current is None:continue
        m=DE.match(s)
        if m:
            current['stem'] += (' ' if current['stem'] else '')+s[m.end():].strip()
        elif m:=ANS.match(s):
            current['answer'] += (' ' if current['answer'] else '') + s[m.end():].strip()
        elif m:=SOL.match(s):
            current['solution'] += (' ' if current['solution'] else '') + s[m.end():].strip()
        elif not current['stem'] and not current['answer'] and not current['solution'] and not re.match(r'^(?:Mức độ|Cấp độ|Dạng|Phương pháp|Yêu cầu|Lưu ý|Trạng thái|Bộ dạng|Câu hỏi mẫu)\b',s,re.I):
            # Some Word questions have 'Câu 01' on its own Heading2, followed by prose.
            current['stem']=s
        elif current['solution'] and style not in ('Heading1','Heading2','Heading3','Title','Subtitle') and not re.match(r'^(?:Đợt|Phương pháp|Mức độ|Cấp độ|Dạng|Chú ý|Tài liệu)\b',s,re.I):
            # Keep legitimate multi-paragraph solutions, but not following section text.
            if len(current['solution']) < 9000:current['solution']+=' '+s
    if current:yield current


def export(source,outdir,sqlite_path):
    mapping=json.loads(TOPIC_MAP.read_text(encoding='utf8'))
    catalog=json.loads((ROOT/'backend/app/ai/knowledge/index.json').read_text(encoding='utf8'))
    by_grade={int(g):{t['id'] for t in ts} for g,ts in catalog.items()}
    expected={v['source_word']: (int(k),v) for k,v in mapping.items()}
    existing=get_existing_signatures()
    inside=set()
    outdir.mkdir(parents=True,exist_ok=True)
    if sqlite_path.exists():sqlite_path.unlink()
    db=sqlite3.connect(sqlite_path)
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=OFF')
    db.execute('''CREATE TABLE questions(id TEXT PRIMARY KEY,grade INTEGER NOT NULL,topic TEXT NOT NULL,
       difficulty TEXT NOT NULL,question_type TEXT NOT NULL,question TEXT NOT NULL,
       answer TEXT NOT NULL,solution TEXT NOT NULL,options TEXT NOT NULL,source TEXT NOT NULL,
       status TEXT NOT NULL,source_word TEXT NOT NULL,source_question_number INTEGER NOT NULL,
       prompt_hash TEXT NOT NULL UNIQUE)''')
    db.execute('CREATE INDEX ix_word_search ON questions(grade,topic,difficulty,question_type)')
    stats=collections.Counter()
    per_topic={}
    with zipfile.ZipFile(source) as z:
        all_docs=[n for n in z.namelist() if n.endswith('.docx')]
        missing=set(expected)-set(all_docs)
        if missing:raise ValueError('Missing mapped source Word files: '+str(sorted(missing)[:3]))
        for number,path in enumerate(all_docs,1):
            if path not in expected:raise ValueError('Unexpected Word filename: '+path)
            source_no, info=expected[path]
            grade=int(info['grade']);topic=str(info['topic'])
            # Some playable practice topics (chia_du, chia_het, phuong_trinh_bac_hai)
            # are in the imported B56 mapping but not the AI knowledge index.
            # Keep their exact IDs; never silently remap to unrelated topics.
            if topic not in by_grade[grade]:stats['word_topics_not_in_ai_catalog']+=1
            output=outdir/f'{source_no:03d}_toan_{grade}_{topic}.jsonl'
            doc_stats=collections.Counter()
            with output.open('w',encoding='utf8') as handle:
                for seq,item in enumerate(enumerate_items(paragraphs(z.read(path))),1):
                    doc_stats['question_markers']+=1;stats['question_markers']+=1
                    stem,opts=split_options(item['stem'])
                    answer,kind=normalize_answer(item['answer'],opts)
                    row={'id':f'word_{source_no:03d}_{seq:04d}', 'grade':grade,'topic':topic,
                         'topic_name':info['name'],'question_type':kind,'difficulty':'medium',
                         'question':stem,'answer':answer,'solution':item['solution'],
                         'options':opts if kind=='multiple_choice' else [],
                         'source_word':path,'source_question_number':item['number'],
                         'quality_status':'candidate_unverified'}
                    hashvalue=sha_prompt(stem) if stem else ''
                    status='eligible_candidate'
                    if not stem or len(stem)<8 or len(stem)>1800 or not answer or len(answer)>250 or len(item['solution'])<12 or len(item['solution'])>2800:
                        status='incomplete_fields'
                    elif kind=='unusable_mcq':status='invalid_mcq'
                    elif kind=='multiple_choice' and (len(set(canonical(o) for o in opts))!=4 or answer not in opts):status='invalid_mcq'
                    elif hashvalue in existing:status='duplicate_existing_bank'
                    elif hashvalue in inside:status='duplicate_word_bank'
                    row['import_status']=status
                    row['prompt_hash']=hashvalue
                    handle.write(json.dumps(row,ensure_ascii=False)+'\n')
                    doc_stats[status]+=1;stats[status]+=1
                    if status=='eligible_candidate':
                        inside.add(hashvalue)
                        db.execute('''INSERT INTO questions(id,grade,topic,difficulty,question_type,question,answer,solution,options,source,status,source_word,source_question_number,prompt_hash)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
                            row['id'],grade,topic,'medium',kind,stem,answer,item['solution'],
                            json.dumps(row['options'],ensure_ascii=False), '150_CHU_DE_WORD',
                            'candidate_unverified',path,item['number'],hashvalue))
            per_topic[str(source_no)]={'grade':grade,'topic':topic,'name':info['name'],**doc_stats}
            if number%25==0:print('Imported',number,'/',len(all_docs),'raw',stats['question_markers'],'active',stats['eligible_candidate'],flush=True)
    db.commit()
    ok=db.execute('PRAGMA quick_check').fetchone()[0]
    if ok!='ok':raise RuntimeError('SQLite check:'+ok)
    db.close()
    report={'word_files':len(expected),'stats':dict(stats),'per_topic':per_topic,'eligibility':'structural_only_not_independent_math_certification',
        'source':str(source),'db_sha256':hashlib.sha256(sqlite_path.read_bytes()).hexdigest(),'db_bytes':sqlite_path.stat().st_size}
    (STORAGE/'v60_word_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--output-dir');ns=ap.parse_args()
    result=export(Path(ns.source),Path(ns.output_dir) if ns.output_dir else ROOT/'question_bank_word_v60',STORAGE/'v60_word_candidates.sqlite')
    print(json.dumps({'files':result['word_files'],'stats':result['stats'],'db_bytes':result['db_bytes']},ensure_ascii=False,indent=2))
