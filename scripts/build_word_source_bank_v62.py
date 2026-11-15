#!/usr/bin/env python3
"""Build a read-only, source-faithful question bank from the 150 supplied Word files.

The original Word ZIP and V254/V59/V60 data remain untouched. Each Word is mapped
via its explicit numeric source ID and the audited V61 topic manifest, not a
filename guess. Keep unapproved entries in the JSONL exports for review but do
not insert them into the serveable SQLite question table.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sqlite3
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from import_word_question_bank_v60 import paragraphs, enumerate_items, normalize_answer, split_options

STORAGE = ROOT / 'backend/app/ai/storage'
MAPPING_FILE = STORAGE / 'v254_b56_topic_map.json'
FORM_RE = re.compile(r'^([A-Z]{1,5}\d{2}-\d{3})\s*[|·-]\s*(.+)$')
LEVEL_RE = re.compile(r'^Mức\s*độ\s*[:：]\s*(.*)', re.I)
Q_RE = re.compile(r'^Câu\s*(?:hỏi\s*)?(?:số\s*)?0*(\d+)\b', re.I)


def canonical(value):
    from app.ai.engine.question_identity import normalize_question_text
    return normalize_question_text(value)


def prompt_key(value):
    from app.ai.engine.question_identity import question_key
    return question_key(value)


def source_metadata(paras):
    """Recover form/difficulty from Word section headings, not question filename."""
    result = []
    current_form, current_title, current_level = '', '', 'medium'
    for style, line in paras:
        fm = FORM_RE.match(line)
        if fm:
            current_form, current_title = fm.group(1), fm.group(2)
        lv = LEVEL_RE.match(line)
        if lv:
            text = lv.group(1).casefold()
            if 'nền tảng' in text or 'cơ bản' in text:
                current_level = 'easy'
            elif 'nâng cao' in text or 'khó' in text:
                current_level = 'hard'
            else:
                current_level = 'medium'
        if Q_RE.match(line):
            result.append((current_form, current_title, current_level))
    return result


def valid_fields(stem, answer, solution, kind, opts):
    if not (8 <= len(stem) <= 1800 and 1 <= len(answer) <= 250 and 12 <= len(solution) <= 2800):
        return 'incomplete_fields'
    if kind == 'unusable_mcq':
        return 'invalid_mcq'
    if kind == 'multiple_choice':
        if len(opts) != 4 or len({canonical(x) for x in opts}) != 4 or answer not in opts:
            return 'invalid_mcq'
        # Check supported arithmetic/elementary polynomial equivalence when possible.
        from app.ai.engine.validator import options_equivalent
        for i, option in enumerate(opts):
            for other in opts[i + 1:]:
                if options_equivalent(option, other):
                    return 'equivalent_mcq_options'
    return 'usable_candidate'


def build(source: Path, outdir: Path, db_path: Path, report_path: Path):
    mapping = json.loads(MAPPING_FILE.read_text(encoding='utf-8'))
    index = json.loads((ROOT / 'backend/app/ai/knowledge/index.json').read_text(encoding='utf-8'))
    allowed = {int(grade): {topic['id'] for topic in topics} for grade, topics in index.items()}
    expected = {f'{int(n):03d}': (int(n), entry) for n, entry in mapping.items()}
    stats, per_topic = collections.Counter(), {}
    seen = set()
    outdir.mkdir(parents=True, exist_ok=True)
    if db_path.exists(): db_path.unlink()
    connection = sqlite3.connect(str(db_path))
    connection.executescript('''
       PRAGMA journal_mode=DELETE;
       PRAGMA synchronous=OFF;
       CREATE TABLE questions (
           id TEXT PRIMARY KEY,grade INTEGER NOT NULL,topic TEXT NOT NULL,difficulty TEXT NOT NULL,
           question_type TEXT NOT NULL,question TEXT NOT NULL,answer TEXT NOT NULL,solution TEXT NOT NULL,
           options TEXT NOT NULL,source TEXT NOT NULL,status TEXT NOT NULL,source_word TEXT NOT NULL,
           source_question_number INTEGER NOT NULL,prompt_hash TEXT NOT NULL UNIQUE,
           form_id TEXT NOT NULL,form_title TEXT NOT NULL);
       CREATE INDEX ix_word62_topic ON questions(grade, topic, difficulty, question_type);
       CREATE INDEX ix_word62_grade_type ON questions(grade, question_type);
    ''')
    ins = '''INSERT INTO questions(id,grade,topic,difficulty,question_type,question,answer,
        solution,options,source,status,source_word,source_question_number,prompt_hash,form_id,form_title)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    try:
        with zipfile.ZipFile(source) as archive:
            word_paths = sorted(n for n in archive.namelist() if n.lower().endswith('.docx'))
            if len(word_paths) != 150 or len(mapping) != 150:
                raise ValueError(f'Required 150 Word/topic maps, got {len(word_paths)} Word/{len(mapping)} maps')
            used = set()
            for name in word_paths:
                name_only = Path(name).name
                match = re.match(r'^(\d{3})_', name_only)
                if not match or match.group(1) not in expected:
                    raise ValueError('Unmapped Word source: ' + name)
                source_num, topic_info = expected[match.group(1)]
                if source_num in used:
                    raise ValueError('Repeated topic source number: ' + str(source_num))
                used.add(source_num)
                if name not in (topic_info.get('source_word'),topic_info.get('source_word_legacy')):
                    raise ValueError('Word filename does not match audited mapping: ' + name)
                grade = int(topic_info['grade'])
                topic = str(topic_info['topic'])
                if source_num <= 50 and grade != 10 or 51 <= source_num <= 100 and grade != 11 or source_num > 100 and grade != 12:
                    raise ValueError(f'Inconsistent grade/source number: {source_num} / {grade}')
                if topic not in allowed[grade] and topic not in ('chia_du','chia_het','phuong_trinh_bac_hai'):
                    raise ValueError('Out-of-catalog Word topic: ' + topic)
                doc_paras = list(paragraphs(archive.read(name)))
                meta = source_metadata(doc_paras)
                items = list(enumerate_items(doc_paras))
                if len(meta) != len(items):
                    raise ValueError(f'Question metadata missing for {name}: {len(meta)} != {len(items)}')
                docstats = collections.Counter()
                export_path = outdir / f'{source_num:03d}_toan_{grade}_{topic}.jsonl'
                with export_path.open('w', encoding='utf-8') as out:
                    for seq, (item, (form_id, form_title, difficulty)) in enumerate(zip(items, meta),1):
                        stem, opts = split_options(item['stem'])
                        ans, kind = normalize_answer(item['answer'], opts)
                        stem, ans, solution = stem.strip(), ans.strip(), item['solution'].strip()
                        status = valid_fields(stem, ans, solution, kind, opts)
                        sig = prompt_key(stem) if stem else ''
                        if status == 'usable_candidate' and sig in seen:
                            status = 'duplicate_word_source'
                        if status == 'usable_candidate':
                            seen.add(sig)
                        row = {
                            'id':f'word62_{source_num:03d}_{seq:04d}',
                            'grade':grade,'topic':topic,'topic_name':topic_info['name'],
                            'difficulty':difficulty,'form_id':form_id,'form_title':form_title,
                            'question_type':kind,'question':stem,'answer':ans,
                            'solution':solution,'options':opts if kind=='multiple_choice' else [],
                            'source_word':topic_info['source_word'],
                            'source_question_number':int(item['number']),
                            'source':'150_CHU_DE_WORD(1).zip','quality_status':'candidate_unverified',
                            'import_status':status,'prompt_hash':sig
                        }
                        out.write(json.dumps(row, ensure_ascii=False)+'\n')
                        docstats[status] += 1
                        stats[status] += 1
                        if status == 'usable_candidate':
                            connection.execute(ins,(
                                row['id'],grade,topic,difficulty,kind,stem,ans,solution,
                                json.dumps(row['options'],ensure_ascii=False),'150_CHU_DE_WORD','candidate_unverified',
                                row['source_word'],int(item['number']),sig,form_id,form_title
                            ))
                per_topic[str(source_num)] = {'grade':grade,'topic':topic,'name':topic_info['name'],
                                               'export':export_path.name,**docstats}
                stats['word_files'] += 1
                if source_num % 25 == 0:
                    connection.commit()
                    print(f'Word {source_num}/150, usable {stats["usable_candidate"]}', flush=True)
        connection.commit()
        qc = connection.execute('PRAGMA quick_check').fetchone()[0]
        if qc != 'ok': raise RuntimeError('SQLite integrity error: '+qc)
        bank_rows = connection.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
        coverage = connection.execute('SELECT COUNT(*) FROM (SELECT grade,topic FROM questions GROUP BY grade,topic)').fetchone()[0]
        types = dict(connection.execute('SELECT question_type, COUNT(*) FROM questions GROUP BY question_type'))
        levels = dict(connection.execute('SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty'))
        connection.close()
        source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        db_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()
        summary = {
            'source_filename':source.name,'source_sha256':source_sha,'source_files':stats['word_files'],
            'raw_question_markers':sum(stats[k] for k in ('usable_candidate','duplicate_word_source','incomplete_fields','invalid_mcq','equivalent_mcq_options')),
            'usable_questions':bank_rows,'covered_source_topics':coverage,'question_types':types,
            'difficulty_counts':levels,'status_counts':dict(stats),'per_topic':per_topic,
            'db_sha256':db_sha,'db_bytes':db_path.stat().st_size,
            'quality_status':'candidate_unverified: structure/duplicate checks; not all answers independently verified',
            'source_retention':'Word ZIP unchanged, V254/V59/V60/V61 unchanged'
        }
        report_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
        return summary
    finally:
        connection.close()


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    args=ap.parse_args()
    import sys
    sys.path.insert(0,str(ROOT/'backend'))
    result=build(args.source,ROOT/'question_bank_word_v62',STORAGE/'v62_word_source.sqlite',STORAGE/'v62_word_source_manifest.json')
    print(json.dumps({k:result[k] for k in ('source_files','raw_question_markers','usable_questions','covered_source_topics','status_counts','difficulty_counts','question_types')},ensure_ascii=False,indent=2))
