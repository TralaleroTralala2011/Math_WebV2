import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from database.data_paths import database_path, LEGACY_DIR
from scripts.backup_sqlite import backup_all

class PersistentDataTests(unittest.TestCase):
    def test_legacy_path(self):
        with patch.dict(os.environ, {'MATHWEB_DATA_DIR': ''}):
            self.assertEqual(database_path('mathweb.db'), LEGACY_DIR / 'mathweb.db')
    def test_external_path(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'MATHWEB_DATA_DIR': d}):
            self.assertEqual(database_path('mathweb.db'), Path(d) / 'mathweb.db')
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError): database_path('../bad.db')
    def test_live_wal_backup_and_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); source=root/'live'; source.mkdir()
            db=source/'mathweb.db'
            with sqlite3.connect(db) as c:
                c.execute('PRAGMA journal_mode=WAL')
                c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, xp INTEGER)')
                c.execute('INSERT INTO users VALUES(1,42)')
            snap=backup_all(source,root/'backups')
            with sqlite3.connect(snap/'mathweb.db') as c:
                self.assertEqual(c.execute('SELECT xp FROM users').fetchone()[0],42)
                self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertTrue((snap/'manifest.json').is_file())
    def test_backup_inside_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): backup_all(Path(d),Path(d)/'backup')

if __name__ == '__main__': unittest.main()
