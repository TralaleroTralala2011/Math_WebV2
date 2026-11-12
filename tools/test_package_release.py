"""Tests for release data guard; isolated toy database only."""
import importlib.util
from pathlib import Path
import sqlite3
from zipfile import ZipFile

import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v154_package_release',HERE/'package_release.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture(tmp_path):
    root=tmp_path/'source'/'MATH_WEB_GITHUB_READY'
    db=root/'backend/database/mathweb.db'
    db.parent.mkdir(parents=True)
    with sqlite3.connect(db) as c:
        c.execute('CREATE TABLE users (username TEXT)')
        c.execute("INSERT INTO users VALUES ('private')")
    (root/'index.html').write_text('<h1>safe source</h1>')
    z=tmp_path/'original.zip'
    with ZipFile(z,'w') as pack:
        pack.write(db,'MATH_WEB_GITHUB_READY/backend/database/mathweb.db')
    return root,db,z


def test_public_zip_strips_private_db_private_checkpoint_preserves_it(tmp_path):
    root,db,z=fixture(tmp_path)
    out=mod.pack(root,z,tmp_path/'release','V154')
    assert out['sqlite_files_preserved_exactly']
    assert out['output']['MATH_WEB_GITHUB_READY_V154_PRIVATE_CHECKPOINT.zip']['sqlite_files']==1
    assert out['output']['MATH_WEB_GITHUB_READY_V154_GITHUB_SOURCE_ONLY.zip']['sqlite_files']==0
    with ZipFile(tmp_path/'release/MATH_WEB_GITHUB_READY_V154_GITHUB_SOURCE_ONLY.zip') as safe:
        assert 'MATH_WEB_GITHUB_READY/index.html' in safe.namelist()
        assert all(not name.endswith('.db') for name in safe.namelist())
    with pytest.raises(FileExistsError):
        mod.pack(root,z,tmp_path/'release','V154')


def test_refuse_modified_or_new_sqlite(tmp_path):
    root,db,z=fixture(tmp_path)
    db.write_bytes(db.read_bytes()+b'corrupt')
    with pytest.raises(ValueError,match='byte-preserved'):
        mod.pack(root,z,tmp_path/'release','V154')
    # Restore and create a second unexpected DB: hard fail rather than leaking it.
    with ZipFile(z) as src:
        db.write_bytes(src.read('MATH_WEB_GITHUB_READY/backend/database/mathweb.db'))
    extra=root/'backend/database/not-in-input.db'; extra.write_bytes(db.read_bytes())
    with pytest.raises(ValueError,match='Unexpected SQLite'):
        mod.pack(root,z,tmp_path/'release','V154')


def test_nonempty_wal_refused_before_publication(tmp_path):
    root,db,z=fixture(tmp_path)
    (db.parent/(db.name+'-wal')).write_bytes(b'unsafe pending transaction')
    with pytest.raises(ValueError,match='Nonempty SQLite WAL'):
        mod.pack(root,z,tmp_path/'release','V155')
    assert not (tmp_path/'release/MATH_WEB_GITHUB_READY_V155_PRIVATE_CHECKPOINT.zip').exists()


def test_env_example_preserved_and_empty_wal_skipped(tmp_path):
    root,db,z=fixture(tmp_path)
    (db.parent/(db.name+'-wal')).write_bytes(b'')
    (db.parent/(db.name+'-shm')).write_bytes(b'reconstructible cache')
    (root/'.env.mathweb.example').write_text('QF_ADMIN_TOKEN=REPLACE_WITH_A_LONG_RANDOM_SECRET')
    (root/'.env.production').write_text('QF_ADMIN_TOKEN=PRIVATE_TEST_VALUE')
    mod.pack(root,z,tmp_path/'release','V155')
    for fname in ['MATH_WEB_GITHUB_READY_V155_PRIVATE_CHECKPOINT.zip',
                  'MATH_WEB_GITHUB_READY_V155_GITHUB_SOURCE_ONLY.zip']:
        with ZipFile(tmp_path/'release'/fname) as archive:
            assert all(not n.endswith(('-wal','-shm')) for n in archive.namelist())
    with ZipFile(tmp_path/'release/MATH_WEB_GITHUB_READY_V155_GITHUB_SOURCE_ONLY.zip') as archive:
        assert 'MATH_WEB_GITHUB_READY/.env.mathweb.example' in archive.namelist()
        assert 'MATH_WEB_GITHUB_READY/.env.production' not in archive.namelist()
