"""Run: python -m question_factory.cli --db data/qf.sqlite3 ..."""
import argparse
import json
from . import storage, worker
from .bootstrap import initialize_factory, database_path


def main(argv=None):
    p=argparse.ArgumentParser(description='MATH_WEB Question Factory pilot')
    p.add_argument('--db',default=database_path())
    commands=p.add_subparsers(dest='command',required=True)
    for cmd in ['init','seed-demo','seed-curated','seed-v114','seed-v116','seed-v117','seed-v118','seed-v119','status','pause','resume']:
        commands.add_parser(cmd)
    a=commands.add_parser('approve-type');a.add_argument('type_id');a.add_argument('--reviewer',required=True)
    a=commands.add_parser('enqueue');a.add_argument('--per-type',type=int,default=10)
    a=commands.add_parser('run');a.add_argument('--workers',type=int,default=4);a.add_argument('--max-jobs',type=int,default=0)
    a=commands.add_parser('daemon');a.add_argument('--workers',type=int,default=4);a.add_argument('--poll',type=float,default=5)
    a=commands.add_parser('limit');a.add_argument('max_verified',type=int)
    a=commands.add_parser('cost-ceiling');a.add_argument('limit_cents',type=int)
    a=commands.add_parser('import-topics');a.add_argument('json_file');a.add_argument('--expected',type=int,default=150)
    a=p.parse_args(argv)
    initialize_factory(a.db)
    if a.command=='seed-demo': storage.seed_samples(a.db)
    elif a.command=='seed-curated': print('Registered candidate methods:',storage.seed_curated(a.db))
    elif a.command=='seed-v114': print('Registered V114 candidate methods:',storage.seed_v114(a.db))
    elif a.command=='seed-v116': print('Registered V116 candidate methods:',storage.seed_v116(a.db))
    elif a.command=='seed-v117': print('Registered V117 candidate methods:',storage.seed_v117(a.db))
    elif a.command=='seed-v118': print('Registered V118 candidate methods:',storage.seed_v118(a.db))
    elif a.command=='seed-v119': print('Registered V119 candidate methods:',storage.seed_v119(a.db))
    elif a.command=='approve-type': storage.approve(a.db,a.type_id,a.reviewer)
    elif a.command=='enqueue': print('Enqueued:',storage.enqueue(a.db,a.per_type))
    elif a.command=='run': print('Processed jobs:',worker.run(a.db,workers=a.workers,max_jobs=a.max_jobs))
    elif a.command=='daemon': worker.serve_forever(a.db,workers=a.workers,poll_seconds=a.poll)
    elif a.command=='pause': storage.set_paused(a.db,True)
    elif a.command=='resume': storage.set_paused(a.db,False)
    elif a.command=='limit': storage.set_limit(a.db,a.max_verified)
    elif a.command=='cost-ceiling': storage.set_cost_limit(a.db,a.limit_cents)
    elif a.command=='import-topics':
        from .topic_import import import_topics
        print('Imported:',import_topics(a.db,a.json_file,a.expected))
    print(json.dumps(storage.progress(a.db),ensure_ascii=False,indent=2))

if __name__=='__main__': main()
