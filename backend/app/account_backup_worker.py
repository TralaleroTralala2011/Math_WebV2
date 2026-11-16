"""Periodic safe restore-point snapshots for a single-worker persistent backend.

Retained snapshots live on the same disk; operators must also keep independent
encrypted backups. Stops when FastAPI shuts down, never restores automatically.
"""
import logging
import os
from threading import Event, Thread

from database.database import DATABASE_PATH
from database.persistence_guard import create_snapshot

stop_event = Event()
_thread = None


def start_account_backup_worker():
    global _thread
    if not (os.getenv('MATHWEB_DATA_DIR') or os.getenv('MATHWEB_ENABLE_LOCAL_BACKUPS')):
        return
    if _thread and _thread.is_alive():
        return
    stop_event.clear()

    def routine():
        while not stop_event.wait(3600):
            try:
                create_snapshot(DATABASE_PATH, min_age_hours=6, max_snapshots=4)
            except Exception:
                logging.getLogger('mathweb.backups').exception('Account restore-point snapshot failed; check disk space')

    _thread = Thread(name='mathweb-account-snapshots', target=routine, daemon=True)
    _thread.start()


def stop_account_backup_worker():
    global _thread
    stop_event.set()
    if _thread and _thread.is_alive():
        _thread.join(timeout=3)
    _thread = None
