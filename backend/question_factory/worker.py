"""Bounded concurrent workers. Resumable and idempotent over a local SQLite DB."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import uuid
import logging
import signal
from . import engine, storage


def process_one(path, owner, *, lease_sec=120):
    con=storage.connect(path)
    try:
        job=storage.claim(con,owner,lease_sec=lease_sec)
        if job is None:
            return False
        try:
            record=con.execute("SELECT family,difficulty,topic_id,id FROM archetypes WHERE id=?",
                               (job['archetype_id'],)).fetchone()
            if record is None:
                raise RuntimeError('unknown type')
            for ordinal in range(job['desired']):
                if storage.is_paused(con):
                    storage.defer(con,job['id'],owner,'paused')
                    return True
                if not storage.heartbeat(con,job['id'],owner,lease_sec=lease_sec):
                    raise RuntimeError('lease expired or changed')
                q=engine.generate(record['family'],ordinal,record['difficulty'],
                                  seed_key=f"{record['topic_id']}:{record['id']}")
                good,details=engine.independently_verify(q)
                storage.store_question(con,job['id'],owner,q,good,details)
                if not good:
                    raise RuntimeError(f'question rejected by verifier at ordinal {ordinal}')
            storage.finish(con,job['id'],owner)
            return True
        except storage.LimitReached as e:
            storage.defer(con,job['id'],owner,e)
            return True
        except Exception as e:
            storage.fail(con,job['id'],owner,e)
            return True
    finally:
        con.close()


def run(path, workers=4, max_jobs=0):
    if not 1<=workers<=16:
        raise ValueError('workers must be between 1 and 16')
    if max_jobs<0:
        raise ValueError('max_jobs must be >=0')
    counter=0
    lock=threading.Lock()
    # An empty queue ends the run. For a persistent daemon, call the CLI loop.
    def work():
        nonlocal counter
        owner=f'{uuid.uuid4().hex}-{threading.get_ident()}'
        while True:
            with lock:
                if max_jobs and counter>=max_jobs:
                    return
                if max_jobs: counter+=1
            claimed=process_one(path,owner)
            if not claimed:
                if max_jobs:
                    with lock: counter-=1
                return
            if not max_jobs:
                with lock: counter+=1
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(lambda _:work(),range(workers)))
    return counter


def serve_forever(path,workers=4,poll_seconds=5):
    """Single-host daemon with graceful stops and bounded error recovery.

    A process supervisor such as Docker/systemd restarts this daemon on a
    process-level failure. Each job lease is persisted in SQLite so a crashed
    daemon doesn't lose a completed checkpoint.
    """
    if not (1 <= workers <= 16) or poll_seconds < 0.5:
        raise ValueError('invalid daemon settings')
    stop=threading.Event()
    def request_stop(_signum,_frame):
        stop.set()
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM,request_stop)
        signal.signal(signal.SIGINT,request_stop)
    log=logging.getLogger(__name__)
    consecutive_errors=0
    while not stop.is_set():
        try:
            run(path,workers=workers)
            consecutive_errors=0
            interval=poll_seconds
        except Exception:
            consecutive_errors+=1
            interval=min(60.0,poll_seconds*2**min(consecutive_errors,4))
            log.exception('Factory daemon iteration failed; retrying')
        stop.wait(interval)
