#!/usr/bin/env python3
"""Fix unambiguous INVALID legacy topic IDs in V196 bank only.
Protects question/answer text and stores a reversible ledger. Excludes
ambiguous `chia_het` with no matching canonical topic in the 150 catalog.
"""
import sqlite3,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
DB=BASE/'backend/database/mathweb.db'
REMAP={(10,'vecto'):'vector',(11,'xac_suat'):'xac_suat_11',
       (12,'ham_mu_logarit'):'pt_logarit',(12,'toa_do_oxyz'):'g12_geom_point_plane_distance'}


def main():
    idx=json.loads((BASE/'backend/app/ai/knowledge/index.json').read_text())
    valid={(int(g),r['id']) for g,rs in idx.items() for r in rs}
    assert all((g,t) in valid for (g,_),t in REMAP.items())
    with sqlite3.connect(DB) as db:
        before=db.execute('SELECT count(*) FROM admin_question_bank').fetchone()[0]
        db.execute('BEGIN IMMEDIATE')
        db.execute('''CREATE TABLE IF NOT EXISTS mathweb_v198_topic_repair_ledger
             (bank_id INTEGER PRIMARY KEY, grade INTEGER, old_topic TEXT, new_topic TEXT)''')
        edited=0
        for (grade,old),new in REMAP.items():
            rows=db.execute('select id from admin_question_bank where grade=? and topic=?',(grade,old)).fetchall()
            for (id_,) in rows:
                existing=db.execute('select old_topic,new_topic from mathweb_v198_topic_repair_ledger where bank_id=?',(id_,)).fetchone()
                assert existing is None, ('already remapped',id_)
                db.execute('insert into mathweb_v198_topic_repair_ledger values(?,?,?,?)',(id_,grade,old,new))
                db.execute('update admin_question_bank set topic=? where id=? and topic=?',(new,id_,old))
                assert db.execute('select topic from admin_question_bank where id=?',(id_,)).fetchone()[0]==new
                edited+=1
        assert db.execute('SELECT count(*) FROM admin_question_bank').fetchone()[0]==before
        assert db.execute('pragma quick_check').fetchone()[0]=='ok'
        db.commit()
        print(json.dumps({'remapped_question_rows':edited,'bank_before_after':before,
           'ambiguous_chia_het_left_untouched':db.execute("select count(*) from admin_question_bank where grade=10 and topic='chia_het'").fetchone()[0],
           'entries':db.execute('select old_topic,new_topic,count(*) from mathweb_v198_topic_repair_ledger group by old_topic,new_topic').fetchall()},ensure_ascii=False))

if __name__=='__main__':main()
