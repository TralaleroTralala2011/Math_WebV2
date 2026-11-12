#!/usr/bin/env python3
"""Import structurally checked V179/V180 questions into the *actual* Admin bank.

No database is created, and no write happens without --write and a fresh --backup.
Do not count this import as independent mathematical form certification.

Example (from project root):
  python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db
  python backend/scripts/import_bank_updates.py --db backend/database/mathweb.db \
      --write --backup backups/mathweb-before-v181.sqlite
"""
from __future__ import annotations
import argparse
import contextlib
import datetime
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))
from app.ai.engine.validator import validate, ValidationError
from app.questions.answer_checker import grade_answer

DEFAULT_INPUT = PROJECT_ROOT / 'bank_updates' / 'V181_IMPORT_READY.jsonl'
REQUIRED_COLUMNS = {
    'grade', 'topic', 'difficulty', 'question_type', 'game_id', 'question',
    'choices_json', 'correct_answer', 'explanation', 'source', 'tags_json',
    'created_by', 'created_at', 'updated_at',
}


def canonical(text):
    return ' '.join(str(text).casefold().split())


def digest(row):
    payload = [row['id'], row['grade'], row['topic'], canonical(row['question']),
               row['answer'], row['solution'], row['question_type'], row.get('choices') or []]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load_and_validate(path):
    catalog = json.loads((PROJECT_ROOT / 'backend/app/ai/knowledge/index.json').read_text(encoding='utf-8'))
    valid_topics = {(int(grade), t['id']) for grade, topics in catalog.items() for t in topics}
    seen_ids, seen_prompts = set(), set()
    records = []
    with path.open(encoding='utf-8') as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            rid = str(row['id'])
            if rid in seen_ids:
                raise ValueError(f'duplicate source ID at line {line_number}: {rid}')
            seen_ids.add(rid)
            if (row['grade'], row['topic']) not in valid_topics:
                raise ValueError(f'unknown grade/topic at line {line_number}: {rid}')
            key = (row['grade'], canonical(row['question']))
            if key in seen_prompts:
                raise ValueError(f'duplicate prompt at line {line_number}: {rid}')
            seen_prompts.add(key)
            if row['question_type'] not in ('multiple_choice', 'short_answer', 'true_false'):
                raise ValueError(f'unsupported question type at line {line_number}: {rid}')
            choices = row.get('choices') or []
            if row['question_type'] == 'short_answer' and choices:
                raise ValueError(f'unexpected short-answer options at line {line_number}: {rid}')
            if row['question_type'] == 'true_false' and (len(choices) != 4 or len(str(row['answer']).split(',')) != 4):
                raise ValueError(f'invalid four-statement true/false at line {line_number}: {rid}')
            candidate = {
                'id': rid, 'grade': row['grade'], 'topic': row['topic'],
                'difficulty': row['difficulty'], 'question_type': row['question_type'],
                'question': row['question'], 'answer': row['answer'],
                'solution': row['solution'], 'options': choices,
                'statements': choices if row['question_type'] == 'true_false' else [],
            }
            try:
                validate(candidate)
            except ValidationError as exc:
                raise ValueError(f'question quality gate at line {line_number}: {rid}: {exc}') from exc
            if not grade_answer(candidate, row['answer']):
                raise ValueError(f'answer grader mismatch at line {line_number}: {rid}')
            if row['question_type'] == 'multiple_choice' and sum(
                bool(grade_answer(candidate, option)) for option in choices
            ) != 1:
                raise ValueError(f'nonunique MCQ answer at line {line_number}: {rid}')
            if len(row['solution'].strip()) < 25:
                raise ValueError(f'answer explanation too short at line {line_number}: {rid}')
            records.append(row)
    return records


def verify_database(conn):
    columns = {col[1] for col in conn.execute('PRAGMA table_info(admin_question_bank)')}
    if not REQUIRED_COLUMNS.issubset(columns):
        raise ValueError(f'not a compatible MATH_WEB Admin bank; missing: {REQUIRED_COLUMNS-columns}')
    if conn.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
        raise ValueError('database failed quick_check')


def existing_id(conn, row):
    # Grade/topic use the existing index prefix. Exact normalized comparison
    # prevents duplicate imports without changing legacy tables or data.
    found = conn.execute(
        'SELECT id FROM admin_question_bank WHERE grade=? AND topic=? '
        'AND lower(trim(question))=lower(trim(?)) LIMIT 1',
        (row['grade'], row['topic'], row['question']),
    ).fetchone()
    return found[0] if found else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True, type=Path, help='existing actual mathweb.db')
    parser.add_argument('--input', default=DEFAULT_INPUT, type=Path)
    parser.add_argument('--write', action='store_true', help='explicitly permit atomic insert')
    parser.add_argument('--backup', type=Path, help='fresh, unused SQLite backup path (required for --write)')
    args = parser.parse_args()
    target = args.db.expanduser().resolve()
    source = args.input.expanduser().resolve()
    if not target.is_file():
        parser.error('target database does not exist; refusing to create a database')
    if not source.is_file():
        parser.error('input JSONL not found')
    if args.write and not args.backup:
        parser.error('--write requires --backup pointing to a NEW path')
    backup = args.backup.expanduser().resolve() if args.backup else None
    if backup and (backup == target or backup.exists()):
        parser.error('backup must be a new path, different from target')
    rows = load_and_validate(source)
    with contextlib.closing(sqlite3.connect(f'file:{target}?mode=ro', uri=True)) as read:
        verify_database(read)
        before = read.execute('SELECT COUNT(*) FROM admin_question_bank').fetchone()[0]
        potential = sum(existing_id(read, r) is None for r in rows)
    summary = {'mode': 'write' if args.write else 'preview', 'db': str(target),
               'input_records': len(rows), 'bank_before': before,
               'potential_new': potential, 'certified_independent_types': 0}
    if not args.write:
        print(json.dumps(summary, ensure_ascii=False))
        return
    assert backup is not None
    backup.parent.mkdir(parents=True, exist_ok=True)
    # Backup uses SQLite's online backup API and includes committed WAL changes.
    with contextlib.closing(sqlite3.connect(str(target), timeout=30)) as db:
        db.execute('PRAGMA busy_timeout=30000')
        verify_database(db)
        with contextlib.closing(sqlite3.connect(str(backup))) as destination:
            db.backup(destination)
            verify_database(destination)
        inserted, already_present = 0, 0
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            db.execute('BEGIN IMMEDIATE')
            db.execute('''CREATE TABLE IF NOT EXISTS mathweb_bank_import_ledger (
                source_id TEXT PRIMARY KEY, bank_id INTEGER NOT NULL,
                payload_sha256 TEXT NOT NULL, imported_at TEXT NOT NULL
            )''')
            for row in rows:
                sha = digest(row)
                prior = db.execute('SELECT payload_sha256 FROM mathweb_bank_import_ledger WHERE source_id=?',
                                   (row['id'],)).fetchone()
                if prior:
                    if prior[0] != sha:
                        raise ValueError(f'conflicting payload for existing source ID: {row["id"]}')
                    already_present += 1
                    continue
                bank_id = existing_id(db, row)
                if bank_id is None:
                    cur = db.execute('''INSERT INTO admin_question_bank
                        (grade,topic,difficulty,question_type,game_id,question,choices_json,
                         correct_answer,explanation,source,tags_json,created_by,created_at,updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                        row['grade'], row['topic'], row['difficulty'], row['question_type'], '',
                        row['question'], json.dumps(row.get('choices') or [], ensure_ascii=False), row['answer'],
                        row['solution'], f'{row["source_bundle"]} QA-gated',
                        json.dumps([str(row.get('source_bundle', 'V181')), row['id'],
                                    'form:' + str(row.get('form_id') or row.get('family') or row['id']),
                                    'method-independence-not-certified',
                                    'semantic-solution-review-pending'], ensure_ascii=False),
                        None, now, now,
                    ))
                    bank_id = cur.lastrowid
                    inserted += 1
                else:
                    already_present += 1
                db.execute('INSERT INTO mathweb_bank_import_ledger VALUES(?,?,?,?)',
                           (row['id'], bank_id, sha, now))
            after = db.execute('SELECT COUNT(*) FROM admin_question_bank').fetchone()[0]
            if after - before != inserted:
                raise AssertionError('before/after count mismatch')
            if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise AssertionError('post-write quick_check failed')
            db.commit()
        except BaseException:
            db.rollback()
            raise
        confirmed = sum(
            db.execute('SELECT COUNT(*) FROM mathweb_bank_import_ledger WHERE source_id IN ('
                       + ','.join('?' for _ in chunk) + ')', chunk).fetchone()[0]
            for chunk in ([r['id'] for r in rows[i:i+400]] for i in range(0, len(rows), 400))
        )
        summary.update(inserted=inserted, already_present=already_present,
                       bank_after=after, ledger_confirmed=confirmed, backup=str(backup),
                       sqlite_integrity='ok')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
