"""Fail-closed SQLite durability policy and non-destructive account restore points.

Render's normal filesystem is ephemeral.  A valid SQLite directory is not
proof of a persistent Render Disk: require the configured directory to be a
mountpoint, rather than creating a fresh user database in the source tree.
No function here deletes a live SQLite database or restores data automatically.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import threading

_LOCK = threading.RLock()


def on_render() -> bool:
    return bool(os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID') or os.getenv('RENDER_EXTERNAL_HOSTNAME'))


def configured_storage(db_path: Path, *, environ=None, mount_check=None) -> dict:
    env = os.environ if environ is None else environ
    hosted = bool(env.get('RENDER') or env.get('RENDER_SERVICE_ID') or env.get('RENDER_EXTERNAL_HOSTNAME'))
    root_string = str(env.get('MATHWEB_DATA_DIR') or '').strip()
    db_string = str(env.get('MATHWEB_DB_PATH') or '').strip()
    root = Path(root_string).expanduser().resolve() if root_string else None
    target = Path(db_path).expanduser().resolve()
    mounted = bool(root and (mount_check or os.path.ismount)(str(root)))
    within = bool(root and target != root and root in target.parents)
    concerns = []
    if hosted:
        if not root:
            concerns.append('Thiếu MATHWEB_DATA_DIR (ổ dữ liệu bền vững).')
        if not db_string:
            concerns.append('Thiếu MATHWEB_DB_PATH.')
        if root and not within:
            concerns.append('MATHWEB_DB_PATH nằm ngoài thư mục dữ liệu đã khai báo.')
        if root and not mounted:
            concerns.append('MATHWEB_DATA_DIR không được nhận diện là ổ đĩa gắn riêng; không được dùng filesystem tạm cho tài khoản.')
    return {
        'render_detected': hosted,
        'mount_verified': mounted,
        'path_matches': within,
        'safe': not concerns,
        'concerns': concerns,
        'db_path': str(target),
        'data_dir': str(root) if root else None,
    }


def enforce_storage(db_path: Path) -> None:
    result = configured_storage(db_path)
    if result['render_detected'] and not result['safe']:
        raise RuntimeError(
            'MATH_WEB DATA PROTECTION: refuse to create an ephemeral account database on Render. '
            + ' '.join(result['concerns'])
            + ' Attach a paid persistent Render Disk and set MATHWEB_DATA_DIR and MATHWEB_DB_PATH '
              'to that mount. Do not redeploy or initialize a new account DB to recover missing users.'
        )


def _guard_dir(db_path: Path) -> Path:
    return db_path.parent / '.mathweb_data_safety'


def _ledger_file(db_path: Path) -> Path:
    return _guard_dir(db_path) / 'user_watermark.json'


def _count_accounts(db_path: Path) -> int | None:
    if not db_path.is_file():
        return None
    try:
        with closing(sqlite3.connect(f'file:{db_path.resolve().as_posix()}?mode=ro', uri=True, timeout=10)) as db:
            has_users = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
            if not has_users:
                return None
            return int(db.execute("SELECT COUNT(*) FROM users WHERE username NOT LIKE 'trial_%' AND username NOT LIKE 'legacy_admin_archived_%'").fetchone()[0])
    except sqlite3.Error as exc:
        raise RuntimeError('Không đọc được dữ liệu tài khoản hiện có. Không tạo database mới để thay thế.') from exc


def _read_ledger(db_path: Path) -> dict | None:
    location = _ledger_file(db_path)
    if not location.exists():
        return None
    try:
        value = json.loads(location.read_text(encoding='utf-8'))
        if not isinstance(value, dict) or not isinstance(value.get('max_users'), int) or value['max_users'] < 0:
            raise ValueError('invalid watermark')
        return value
    except (OSError, ValueError) as exc:
        raise RuntimeError('Hồ sơ an toàn số tài khoản bị hỏng; cần Admin kiểm tra bản sao lưu trước khi khởi động.') from exc


def _atomic_json(destination: Path, payload: dict) -> None:
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix='.ledger-', suffix='.json', dir=destination.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as writer:
            json.dump(payload, writer, ensure_ascii=False, sort_keys=True)
            writer.flush()
            os.fsync(writer.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, destination)
    finally:
        Path(tmp_name).unlink(missing_ok=True)


def check_account_continuity(db_path: Path) -> None:
    """Detect a replaced/empty DB before database init creates fresh accounts."""
    with _LOCK:
        ledger = _read_ledger(db_path)
        if not ledger:
            return
        count = _count_accounts(db_path)
        previous = int(ledger['max_users'])
        if count is None and previous > 0:
            raise RuntimeError(f'MATH_WEB DATA PROTECTION: prior account watermark {previous}, but database is absent or lacks users. Refusing automatic bootstrap. Find and restore old database/backup first.')
        if count is not None and previous >= 2 and count < previous:
            raise RuntimeError(f'MATH_WEB DATA PROTECTION: account count dropped from recorded {previous} to {count}. Refusing to accept a possibly replaced database until audited.')


def record_account_watermark(db_path: Path) -> None:
    """After successful new account registration/initialization, increase only."""
    with _LOCK:
        count = _count_accounts(db_path)
        if count is None:
            return
        old = _read_ledger(db_path) or {}
        peak = max(count, int(old.get('max_users', 0)))
        if old.get('max_users') == peak:
            return
        _atomic_json(_ledger_file(db_path), {
            'format': 'MATHWEB_ACCOUNT_WATERMARK_V1',
            'max_users': peak,
            'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        })


def _list_snapshots(db_path: Path) -> list[Path]:
    path = _guard_dir(db_path) / 'snapshots'
    return sorted(path.glob('accounts-????????T??????Z-*.sqlite3'), reverse=True) if path.is_dir() else []


def snapshot_status(db_path: Path) -> dict:
    count = _count_accounts(db_path)
    ledger = _read_ledger(db_path) or {}
    snaps = _list_snapshots(db_path)
    return {
        'accounts_now': count,
        'accounts_high_watermark': ledger.get('max_users'),
        'snapshot_count': len(snaps),
        'last_snapshot_utc': snaps[0].name[9:25] if snaps else None,
        'backups_on_same_disk_only': True,
    }


def create_snapshot(db_path: Path, *, force=False, max_snapshots=3, min_age_hours=24) -> dict:
    """Consistent WAL-aware backup; never overwrites existing backups or accounts.

    Snapshots are defense against accidental file replacement, NOT against a
    Render Disk disappearing. Admin should also download an encrypted backup.
    """
    with _LOCK:
        check_account_continuity(db_path)
        count = _count_accounts(db_path)
        if count is None:
            return {'created': False, 'reason': 'no_existing_users_table'}
        snaps = _list_snapshots(db_path)
        now = datetime.now(timezone.utc)
        if not force and snaps and now.timestamp() - snaps[0].stat().st_mtime < min_age_hours*3600:
            return {'created': False, 'reason': 'recent_snapshot_exists'}
        folder = _guard_dir(db_path) / 'snapshots'
        folder.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix='.backup-', suffix='.sqlite3', dir=folder)
        os.close(fd)
        tmp = Path(tmp_name)
        try:
            with closing(sqlite3.connect(f'file:{db_path.resolve().as_posix()}?mode=ro', uri=True, timeout=30)) as source:
                with closing(sqlite3.connect(str(tmp), timeout=30)) as target:
                    source.backup(target, pages=1024, sleep=0.05)
            with closing(sqlite3.connect(f'file:{tmp.resolve().as_posix()}?mode=ro', uri=True)) as verification:
                if verification.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                    raise RuntimeError('SQLite snapshot failed quick_check')
            suffix = os.urandom(4).hex()
            final = folder / f"accounts-{now:%Y%m%dT%H%M%SZ}-{suffix}.sqlite3"
            os.chmod(tmp, 0o600)
            os.replace(tmp, final)
        finally:
            tmp.unlink(missing_ok=True)
        # Rotation only touches files the guard created, never the live DB.
        for old in _list_snapshots(db_path)[max_snapshots:]:
            old.unlink(missing_ok=True)
        return {'created': True, 'accounts_in_snapshot': count, 'snapshot_count': len(_list_snapshots(db_path))}
