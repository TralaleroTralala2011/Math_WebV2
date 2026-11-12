"""V154: no private-data merge and no symlink extraction in SQLite backup."""
import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from scripts.backup_sqlite import backup_all
from scripts.migrate_persistent_data import migrate
from scripts.restore_sqlite import restore
from scripts.audit_legacy_databases import audit


def make_db(file: Path, users):
    file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(file) as connection:
        connection.execute('CREATE TABLE users(username TEXT PRIMARY KEY, xp INTEGER)')
        connection.executemany('INSERT INTO users VALUES (?,?)', users)


def test_parallel_accounts_detected_without_names_or_writes(tmp_path):
    first = tmp_path/'backend/database/mathweb.db'
    second = tmp_path/'MATH_WEB/backend/database/mathweb.db'
    make_db(first, [('alice', 500), ('bob', 100)])
    make_db(second, [('alice', 500), ('charlie', 300)])
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in [first, second]]
    report = audit(tmp_path)
    assert report['parallel_db_warning'] is True
    assert report['accounts_bearing_databases'] == 2
    assert report['account_overlap_aggregates'][0]['matching_usernames_count'] == 1
    exported=json.dumps(report)
    assert all(name not in exported for name in ('alice','bob','charlie'))
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in [first, second]] == before


def test_same_account_database_copies_not_marked_distinct(tmp_path):
    first=tmp_path/'backend/database/mathweb.db'
    second=tmp_path/'MATH_WEB/backend/database/mathweb.db'
    make_db(first,[('same', 42)])
    second.parent.mkdir(parents=True)
    second.write_bytes(first.read_bytes())
    assert audit(tmp_path)['parallel_db_warning'] is False


def test_symlinked_sqlite_never_backed_up_or_migrated(tmp_path):
    data=tmp_path/'data'; data.mkdir()
    external=tmp_path/'private.db'; make_db(external,[('private',98)])
    try:
        (data/'other.db').symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip('Symlinks not supported')
    with pytest.raises(ValueError,match='linked'):
        backup_all(data,tmp_path/'backups')
    with pytest.raises(ValueError,match='symbolic'):
        migrate(data,tmp_path/'target',tmp_path/'migration-backups',apply=True)
    assert not (tmp_path/'target').exists()


def test_unsafe_windows_manifest_path_rejected(tmp_path):
    source=tmp_path/'live';source.mkdir()
    make_db(source/'user.db',[('a',3)])
    snap=backup_all(source,tmp_path/'backups')
    manifest=snap/'manifest.json'
    content=json.loads(manifest.read_text())
    content['files'][0]['name']='..\\user.db'
    manifest.write_text(json.dumps(content))
    with pytest.raises(ValueError,match='filename'):
        restore(snap,tmp_path/'target')
    assert not (tmp_path/'target').exists()


def test_backup_refuses_linked_source_directory(tmp_path):
    source=tmp_path/'source';source.mkdir()
    make_db(source/'users.db',[('safe',12)])
    linked=tmp_path/'alias'
    try:
        linked.symlink_to(source, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip('Symlinks not supported')
    with pytest.raises(ValueError,match='symlinked'):
        backup_all(linked,tmp_path/'backups')


def test_refuse_bool_bytes_in_untrusted_manifest(tmp_path):
    source=tmp_path/'source';source.mkdir()
    make_db(source/'users.db',[('safe',12)])
    snap=backup_all(source,tmp_path/'backups')
    manifest=snap/'manifest.json'
    info=json.loads(manifest.read_text())
    info['files'][0]['bytes']=True
    manifest.write_text(json.dumps(info))
    with pytest.raises(ValueError,match='Checksum'):
        restore(snap,tmp_path/'new')


def test_legacy_study_suite_can_migrate_without_overwriting(tmp_path):
    backend=tmp_path/'backend_database'; backend.mkdir()
    main=backend/'mathweb.db'
    extra=tmp_path/'root_data/study_suite.sqlite3'
    make_db(main,[('account_old',50)])
    make_db(extra,[('study_progress',17)])
    hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [main,extra]}
    target=tmp_path/'private_data';backups=tmp_path/'private_backups'
    dry=migrate(backend,target,backups,extra_files=[extra])
    assert dry['mode']=='dry_run' and set(dry['files'])=={'mathweb.db','study_suite.sqlite3'}
    assert not target.exists()
    result=migrate(backend,target,backups,apply=True,extra_files=[extra])
    assert result['mode']=='migrate'
    for file in [main,extra]:
        assert hashlib.sha256(file.read_bytes()).hexdigest()==hashes[file]
        restored=target/file.name
        assert restored.is_file()
        with sqlite3.connect(restored) as con:
            assert con.execute('SELECT COUNT(*) FROM users').fetchone()[0]==1


def test_duplicate_extra_filename_cannot_silently_replace_main(tmp_path):
    backend=tmp_path/'backend'; backend.mkdir()
    a=backend/'mathweb.db'; b=tmp_path/'older/mathweb.db'
    make_db(a,[('new',1)]);make_db(b,[('old',2)])
    with pytest.raises(ValueError,match='Duplicate SQLite filename'):
        migrate(backend,tmp_path/'target',tmp_path/'backups',apply=True,extra_files=[b])
    assert not (tmp_path/'target').exists()
