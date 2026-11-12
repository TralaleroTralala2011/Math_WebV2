#!/usr/bin/env python3
"""Read-only per-topic bank coverage audit against a *real* MATH_WEB SQLite DB.

Counts stored questions only. Does NOT certify mathematical method independence.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'backend/question_factory/catalog_150.json'


def audit(db: Path) -> dict:
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    if len(catalog) != 150 or len({(t['grade'], t['id']) for t in catalog}) != 150:
        raise ValueError('catalog must contain exactly 150 unique grade/topic pairs')
    if not db.is_file():
        raise FileNotFoundError(f'No existing database at {db}')
    con = sqlite3.connect(f'file:{db.resolve()}?mode=ro', uri=True)
    try:
        con.execute('PRAGMA query_only=ON')
        if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='admin_question_bank'").fetchone():
            raise ValueError('Database is not a MATH_WEB Admin bank')
        counts = {(int(g), t): n for g, t, n in con.execute(
            'SELECT grade,topic,COUNT(*) FROM admin_question_bank GROUP BY grade,topic')}
        ledger = bool(con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='mathweb_bank_import_ledger'").fetchone())
        v182 = {}
        if ledger:
            v182 = {(int(g), t): n for g,t,n in con.execute('''
                SELECT b.grade,b.topic,COUNT(*) FROM mathweb_bank_import_ledger l
                JOIN admin_question_bank b ON b.id=l.bank_id
                WHERE l.source_id LIKE 'v182_%' GROUP BY b.grade,b.topic''')}
        per_topic = []
        for topic in catalog:
            k = (int(topic['grade']), topic['id'])
            n = counts.get(k, 0)
            per_topic.append({'grade': k[0], 'topic': k[1], 'name': topic['name'],
                              'stored_questions': n,
                              'raw_question_shortfall_to_2000': max(0, 2000 - n),
                              'v182_imported_questions': v182.get(k, 0) if ledger else None,
                              'certified_independent_types': None,
                              'certified_type_shortfall_to_200': None})
        return {'catalog_topics': len(per_topic), 'topics_with_stored_questions': sum(x['stored_questions']>0 for x in per_topic),
                'total_stored_questions_in_150_topics': sum(x['stored_questions'] for x in per_topic),
                'total_raw_question_shortfall_to_300000': sum(x['raw_question_shortfall_to_2000'] for x in per_topic),
                'certified_independent_types': None,
                'certification_status': 'UNKNOWN: IDs, rows and signatures are not independent mathematical types',
                'production_integration_confirmed': False,
                'per_topic': per_topic}
    finally:
        con.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db', required=True, type=Path)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    report = audit(args.db.expanduser())
    result = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='per_topic'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
