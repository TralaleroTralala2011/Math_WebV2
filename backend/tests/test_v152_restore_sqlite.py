import importlib.util
from pathlib import Path
import sqlite3
import pytest

ROOT = Path(__file__).resolve().parents[1] / 'scripts'
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
backup = load('backup_sqlite')
restore = load('restore_sqlite')

def test_backup_restore_roundtrip(tmp_path):
    source = tmp_path / 'live'; source.mkdir()
    db = source / 'users.db'
    with sqlite3.connect(db) as c:
        c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, xp INTEGER)')
        c.execute('INSERT INTO users VALUES (1, 999)')
    snapshot = backup.backup_all(source, tmp_path / 'backups')
    restored = restore.restore(snapshot, tmp_path / 'restored')
    assert len(restored) == 1
    with sqlite3.connect(restored[0]) as c:
        assert c.execute('SELECT xp FROM users').fetchone() == (999,)

def test_refuse_overwrite(tmp_path):
    source = tmp_path / 'live'; source.mkdir()
    with sqlite3.connect(source / 'users.db') as c:
        c.execute('CREATE TABLE t(x)')
    snapshot = backup.backup_all(source, tmp_path / 'backups')
    target = tmp_path / 'target'; target.mkdir()
    (target / 'important.txt').write_text('keep')
    with pytest.raises(FileExistsError):
        restore.restore(snapshot, target)
    assert (target / 'important.txt').read_text() == 'keep'

def test_tamper_rejected(tmp_path):
    source = tmp_path / 'live'; source.mkdir()
    with sqlite3.connect(source / 'users.db') as c:
        c.execute('CREATE TABLE t(x)')
    snapshot = backup.backup_all(source, tmp_path / 'backups')
    with (snapshot / 'users.db').open('ab') as f:
        f.write(b'tamper')
    with pytest.raises(ValueError, match='Checksum mismatch'):
        restore.restore(snapshot, tmp_path / 'target')
    assert not (tmp_path / 'target').exists()
