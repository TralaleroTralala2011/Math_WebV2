"""Admin update backup/restore: encrypted, complete server-side learner state.

Only named SQLite databases are accepted; the question-bank seed files are
versioned program assets, not mutable user records. Backups contain password
HASHES, never plaintext passwords. No method runs automatically on deploy.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sqlite3
import tempfile
import threading
import zipfile
from datetime import datetime, timezone
from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from fastapi import APIRouter, BackgroundTasks, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse

from database.database import DATABASE_PATH, get_connection
from .admin_routes import audit, require_admin

router = APIRouter(prefix="/api/admin/update", tags=["Admin Update & Backup"])
_BACKUP_MAGIC = b"MWB1"
_CHUNK = 1024 * 1024
_MAX_UPLOAD_BYTES = 512 * 1024 * 1024
_PBKDF2_ROUNDS = 390_000
_RUN_LOCK = threading.Lock()


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _paths() -> dict[str, Path]:
    """Mutable backend stores, including SQLite sidecars via backup API."""
    data_dir = Path(os.environ.get("MATHWEB_DATA_DIR") or Path(__file__).resolve().parents[2] / "database")
    main = Path(DATABASE_PATH)
    from .ai.engine.question_history import _database_path as history_path
    history = history_path()
    return {
        "accounts": main,
        "study_suite": data_dir / "study_suite.sqlite3",
        "learning_progress": data_dir / "learning_progress.sqlite3",
        "final_features": data_dir / "final_features.sqlite3",
        "question_history": history,
    }


def _key(passphrase: str, salt: bytes) -> bytes:
    if len(passphrase) < 12 or len(passphrase) > 200:
        raise ValueError("Mật khẩu tệp sao lưu phải có từ 12 đến 200 ký tự.")
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                      salt=salt, iterations=_PBKDF2_ROUNDS).derive(passphrase.encode("utf-8"))


def _backup_sqlite(source: Path, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    # SQLite backup reads a consistent snapshot, including pending WAL changes.
    with closing(sqlite3.connect(f"file:{source.resolve().as_posix()}?mode=ro", uri=True, timeout=30)) as origin:
        with closing(sqlite3.connect(str(target), timeout=30)) as dest:
            origin.backup(dest, pages=1000, sleep=0.05)
    with closing(sqlite3.connect(f"file:{target.resolve().as_posix()}?mode=ro", uri=True)) as check:
        if check.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("Dữ liệu SQLite sao lưu bị lỗi.")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def create_backup(passphrase: str, output: Path) -> dict:
    """Create encrypted snapshot with integrity manifest. Does not mutate user DB."""
    _key(passphrase, b"0" * 16)  # validate before doing I/O
    with tempfile.TemporaryDirectory(prefix="mw-backup-") as tmp:
        work = Path(tmp)
        manifest = {"format": "MATHWEB_UPDATE_BACKUP_V1", "created_at": _now(), "databases": {}}
        for name, path in _paths().items():
            if not path.is_file():
                if name == "accounts":
                    raise ValueError("Không tìm thấy cơ sở dữ liệu tài khoản để sao lưu.")
                continue
            snap = work / (name + ".sqlite3")
            _backup_sqlite(path, snap)
            manifest["databases"][name] = {"filename": snap.name, "sha256": _sha256(snap), "bytes": snap.stat().st_size}
        zipped = work / "snapshot.zip"
        with zipfile.ZipFile(zipped, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))
            for item in manifest["databases"].values():
                archive.write(work / item["filename"], item["filename"])
        # Streaming AES-256-GCM encryption, so large databases need no large RAM buffer.
        salt, nonce = os.urandom(16), os.urandom(12)
        encryptor = Cipher(algorithms.AES(_key(passphrase, salt)), modes.GCM(nonce)).encryptor()
        encryptor.authenticate_additional_data(_BACKUP_MAGIC)
        with open(output, "wb") as out, open(zipped, "rb") as inp:
            out.write(_BACKUP_MAGIC + salt + nonce)
            for chunk in iter(lambda: inp.read(_CHUNK), b""):
                out.write(encryptor.update(chunk))
            out.write(encryptor.finalize())
            out.write(encryptor.tag)
    return manifest


def _decrypt_backup(source: Path, passphrase: str, dest: Path):
    size = source.stat().st_size
    if size < 4 + 16 + 12 + 16:
        raise ValueError("Tệp sao lưu không hợp lệ hoặc đã bị hỏng.")
    with open(source, "rb") as inp:
        header = inp.read(32)
        if header[:4] != _BACKUP_MAGIC:
            raise ValueError("Đây không phải tệp sao lưu MATH_WEB hợp lệ.")
        salt, nonce = header[4:20], header[20:32]
        inp.seek(-16, os.SEEK_END)
        tag = inp.read(16)
        decryptor = Cipher(algorithms.AES(_key(passphrase, salt)), modes.GCM(nonce, tag)).decryptor()
        decryptor.authenticate_additional_data(_BACKUP_MAGIC)
        inp.seek(32)
        remaining = size - 32 - 16
        try:
            with open(dest, "wb") as out:
                while remaining:
                    chunk = inp.read(min(_CHUNK, remaining))
                    if not chunk:
                        raise ValueError("Tệp sao lưu bị cắt ngắn.")
                    out.write(decryptor.update(chunk))
                    remaining -= len(chunk)
                out.write(decryptor.finalize())
        except Exception as exc:
            dest.unlink(missing_ok=True)
            raise ValueError("Không giải mã được tệp sao lưu. Kiểm tra mật khẩu hoặc tệp đã bị sửa đổi.") from exc


def _validate_archive(zipped: Path, scratch: Path) -> tuple[dict, dict[str, Path]]:
    if not zipfile.is_zipfile(zipped):
        raise ValueError("Dữ liệu giải mã không phải một bản sao lưu ZIP.")
    with zipfile.ZipFile(zipped) as archive:
        if "manifest.json" not in archive.namelist() or len(archive.namelist()) > 8:
            raise ValueError("Manifest sao lưu không hợp lệ.")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("format") != "MATHWEB_UPDATE_BACKUP_V1":
            raise ValueError("Định dạng sao lưu không được hỗ trợ.")
        entries = manifest.get("databases", {})
        if not isinstance(entries, dict) or "accounts" not in entries or not set(entries).issubset(_paths()):
            raise ValueError("Danh sách cơ sở dữ liệu sao lưu không hợp lệ.")
        expected_files = {"manifest.json"} | {name + ".sqlite3" for name in entries}
        if set(archive.namelist()) != expected_files:
            raise ValueError("Có tệp bất thường hoặc thiếu dữ liệu trong bản sao lưu.")
        result = {}
        uncompressed_total = 0
        for name, item in entries.items():
            entry = name + ".sqlite3"
            if not isinstance(item, dict) or item.get("filename") != entry:
                raise ValueError("Tên cơ sở dữ liệu không hợp lệ.")
            info = archive.getinfo(entry)
            uncompressed_total += info.file_size
            if info.file_size > _MAX_UPLOAD_BYTES or info.file_size < 100 or uncompressed_total > _MAX_UPLOAD_BYTES:
                raise ValueError("Kích thước bản sao lưu không hợp lệ.")
            path = scratch / entry
            with archive.open(entry) as src, open(path, "wb") as out:
                shutil.copyfileobj(src, out, _CHUNK)
            if _sha256(path) != item.get("sha256"):
                raise ValueError("Checksum bản sao lưu không khớp.")
            with closing(sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)) as check:
                if check.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise ValueError("Database sao lưu không vượt qua kiểm tra SQLite.")
                if name == "accounts":
                    tables = {r[0] for r in check.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    if not {"users", "admin_accounts", "notifications"}.issubset(tables):
                        raise ValueError("Tệp tài khoản thiếu bảng dữ liệu quan trọng.")
            result[name] = path
    return manifest, result


def restore_backup(upload: Path, passphrase: str) -> dict:
    """Restore all listed stores, with independent rollback snapshots on failure.

    Recommended while the deployment is in maintenance mode and with ONE worker.
    """
    with tempfile.TemporaryDirectory(prefix="mw-restore-") as tmp:
        work = Path(tmp)
        zip_path = work / "payload.zip"
        _decrypt_backup(upload, passphrase, zip_path)
        manifest, snapshots = _validate_archive(zip_path, work)
        paths = _paths()
        rollback = {}
        created = []
        # Validate all input before touching the live database. Make rollback snapshots.
        for name in snapshots:
            path = paths[name]
            if path.exists():
                old = work / (name + "-rollback.sqlite3")
                _backup_sqlite(path, old)
                rollback[name] = old
            else:
                created.append(name)
        written = []
        try:
            for name, data in snapshots.items():
                target = paths[name]
                target.parent.mkdir(parents=True, exist_ok=True)
                with closing(sqlite3.connect(str(data), timeout=30)) as original:
                    with closing(sqlite3.connect(str(target), timeout=30)) as dest:
                        original.backup(dest, pages=1000, sleep=0.05)
                written.append(name)
        except Exception:
            for name in reversed(written):
                if name in rollback:
                    with closing(sqlite3.connect(str(rollback[name]), timeout=30)) as old:
                        with closing(sqlite3.connect(str(paths[name]), timeout=30)) as dest:
                            old.backup(dest)
                elif name in created:
                    paths[name].unlink(missing_ok=True)
            raise
        return {"restored": list(snapshots), "created_at": manifest["created_at"]}


def _record_event(title: str, content: str, actor_id: int, action: str):
    with closing(get_connection()) as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(notifications)")}
        if not {"user_id", "type", "content", "title", "message"}.issubset(cols):
            raise RuntimeError("Bảng notifications chưa được khởi tạo.")
        conn.execute("""INSERT INTO notifications (user_id,type,content,title,message,is_read,created_at)
                        SELECT id,'system_update',?,?,?,0,? FROM users
                        WHERE username NOT LIKE 'legacy_admin_archived_%'""",
                     (content, title, content, _now()))
        audit(conn, actor_id, action, details={"users_notified": conn.execute("SELECT changes()").fetchone()[0]})
        conn.commit()


@router.post("/backup")
def admin_download_backup(background_tasks: BackgroundTasks, passphrase: str = Form(...),
                          authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    if not _RUN_LOCK.acquire(blocking=False):
        raise HTTPException(409, "Có thao tác cập nhật khác đang chạy.")
    fd, temp_name = tempfile.mkstemp(prefix="mathweb-update-", suffix=".mwbackup")
    os.close(fd)
    output = Path(temp_name)
    try:
        create_backup(passphrase, output)
        with closing(get_connection()) as conn:
            audit(conn, admin["id"], "update_backup_export", details={"encrypted": True, "bytes": output.stat().st_size})
            conn.commit()
    except ValueError as exc:
        output.unlink(missing_ok=True)
        raise HTTPException(422, str(exc))
    except Exception:
        output.unlink(missing_ok=True)
        raise
    finally:
        _RUN_LOCK.release()
    background_tasks.add_task(lambda: output.unlink(missing_ok=True))
    return FileResponse(output, media_type="application/octet-stream",
                        filename=f"MATH_WEB_FULL_BACKUP_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.mwbackup",
                        background=background_tasks, headers={"Cache-Control": "no-store, private", "X-Content-Type-Options": "nosniff"})


@router.post("/announce")
def admin_announce_update(authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    # The interface only sends this AFTER browser has initiated a backup download.
    _record_event("MATH_WEB sẽ cập nhật", "Hệ thống đang chuẩn bị cập nhật. Dữ liệu tài khoản được bảo toàn trong bản sao lưu quản trị.",
                  admin["id"], "update_announce")
    return {"ok": True, "message": "Đã gửi thông báo cập nhật đến các tài khoản."}


@router.post("/restore")
async def admin_restore_update(file: UploadFile = File(...), passphrase: str = Form(...),
                               confirmation: str = Form(...), authorization: str | None = Header(default=None)):
    require_admin(authorization)
    if confirmation != "KHOI PHUC DU LIEU":
        raise HTTPException(422, "Cần xác nhận chính xác KHOI PHUC DU LIEU.")
    if not _RUN_LOCK.acquire(blocking=False):
        raise HTTPException(409, "Có thao tác cập nhật khác đang chạy.")
    fd, temp_name = tempfile.mkstemp(prefix="mw-upload-", suffix=".mwbackup")
    os.close(fd)
    tmp = Path(temp_name)
    try:
        size = 0
        with open(tmp, "wb") as dst:
            while True:
                chunk = await file.read(_CHUNK)
                if not chunk: break
                size += len(chunk)
                if size > _MAX_UPLOAD_BYTES:
                    raise HTTPException(413, "Tệp sao lưu vượt quá giới hạn 512 MB.")
                dst.write(chunk)
        try:
            result = restore_backup(tmp, passphrase)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        # After restore, admin IDs/hash may differ; no dependency on old token here.
        with closing(get_connection()) as conn:
            row = conn.execute("SELECT id FROM admin_accounts WHERE username='admin19022011'").fetchone()
        if row:
            _record_event("MATH_WEB đã cập nhật", "Dữ liệu tài khoản và tiến độ học đã được khôi phục từ bản sao lưu.",
                          row["id"], "update_restore")
        return {"ok": True, **result, "message": "Đã khôi phục dữ liệu. Khởi động lại backend và đăng nhập lại để đồng bộ phiên."}
    finally:
        await file.close()
        tmp.unlink(missing_ok=True)
        _RUN_LOCK.release()
