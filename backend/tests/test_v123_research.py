"""V123 isolation tests. Arithmetic checks do not grant method independence."""
import os
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from question_factory import v123_research as qf, storage, engine, operations

class TestV123(unittest.TestCase):
    def test_one_thousand_plus(self):
        self.assertEqual(len(qf.METHODS),1050)
        self.assertEqual(len(qf.FAMILIES),1050)
        self.assertEqual(len({m.topic for m in qf.METHODS}),150)
        self.assertEqual(set(Counter(m.topic for m in qf.METHODS).values()),{7})
        self.assertTrue(all(m.shared_core_method and not m.independence_certified for m in qf.METHODS))

    def test_all_operators_and_oracles(self):
        for name in qf.OPERATIONS:
            m=next(m for m in qf.METHODS if m.operator==name)
            for i in range(10):
                row=engine.generate(m.family,i,'nâng cao')
                self.assertTrue(engine.independently_verify(row)[0],(m.family,i))
                self.assertTrue(row['shared_core_method'])

    def test_tampering(self):
        m=qf.METHODS[0]
        row=engine.generate(m.family,0,'nâng cao')
        row['answer']='999999999'
        self.assertFalse(engine.independently_verify(row)[0])

    def test_no_implicit_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            db=str(Path(folder)/'factory.sqlite3')
            from question_factory.bootstrap import initialize_factory
            initialize_factory(db)
            self.assertEqual(storage.seed_v123(db),1050)
            self.assertEqual(storage.seed_v123(db),1050)
            with storage.connect(db) as con:
                records=con.execute("SELECT COUNT(*) FROM archetypes WHERE id LIKE 'v123_%' AND review_status='pending'").fetchone()[0]
                self.assertEqual(records,1050)
            self.assertEqual(storage.enqueue(db,per_type=10),0)

    def test_all_source_topics(self):
        from question_factory.v121_research import METHODS as old
        self.assertEqual(len(old),300)
        self.assertEqual(len(qf.CATALOG),150)

if __name__=='__main__':unittest.main()
