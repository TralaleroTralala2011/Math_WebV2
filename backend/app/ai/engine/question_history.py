"""Persistent anti-repeat ledger for AI-generated maths questions.

The ledger stores fingerprints and generation metadata only, not personal data.
It survives backend restarts when the application database is persistent.
"""
from __future__ import annotations

import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from .validator import fingerprint


_SCHEMA_LOCK = threading.Lock()
_SCHEMA_READY: set[str] = set()


def _database_path() -> Path:
    """Use a dedicated SQLite file so AI history writes never lock matchmaking.

    Matchmaking intentionally holds a short transaction while it claims queue
    entries. Writing the AI anti-repeat ledger to the same SQLite file from
    inside that flow caused ``database is locked`` when the second player joined.
    The separate ledger remains persistent across restarts and can be relocated
    independently for deployments with persistent disks.
    """
    explicit = os.getenv("MATHWEB_AI_HISTORY_DB_PATH")
    if explicit:
        return Path(explicit).expanduser()

    configured = os.getenv("MATHWEB_DB_PATH")
    if configured:
        main_path = Path(configured).expanduser()
        return main_path.with_name(f"{main_path.stem}_ai_history.sqlite3")

    # backend/app/ai/engine/question_history.py -> backend/database/
    return Path(__file__).resolve().parents[3] / "database" / "mathweb_ai_history.sqlite3"


class QuestionHistory:
    def __init__(self, max_age_days: int = 180):
        self.max_age_seconds = max_age_days * 86400

    def _connect(self):
        path = _database_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path), timeout=10)
        conn.execute("PRAGMA busy_timeout=10000")

        # Schema DDL is done once per database path per process, not on every
        # question-history read/write. This reduces SQLite schema-lock pressure
        # when multiple players request questions concurrently.
        key = str(path.resolve())
        if key not in _SCHEMA_READY:
            with _SCHEMA_LOCK:
                if key not in _SCHEMA_READY:
                    try:
                        conn.execute("""
                            CREATE TABLE IF NOT EXISTS ai_question_history (
                                fingerprint TEXT PRIMARY KEY,
                                topic TEXT NOT NULL DEFAULT '',
                                grade INTEGER NOT NULL DEFAULT 0,
                                difficulty TEXT NOT NULL DEFAULT '',
                                structure_fingerprint TEXT NOT NULL DEFAULT '',
                                variation_key TEXT NOT NULL DEFAULT '',
                                archetype TEXT NOT NULL DEFAULT '',
                                kind TEXT NOT NULL DEFAULT 'question',
                                created_at REAL NOT NULL
                            )
                        """)
                        columns = {row[1] for row in conn.execute("PRAGMA table_info(ai_question_history)").fetchall()}
                        if "variation_key" not in columns:
                            conn.execute("ALTER TABLE ai_question_history ADD COLUMN variation_key TEXT NOT NULL DEFAULT ''")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_history_topic_time ON ai_question_history(topic, created_at DESC)")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_history_kind_time ON ai_question_history(kind, created_at DESC)")
                        conn.commit()
                        _SCHEMA_READY.add(key)
                    except Exception:
                        conn.close()
                        raise
        return conn

    @contextmanager
    def _session(self):
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def recent_fingerprints(self, limit: int = 25000) -> set[str]:
        """Exact questions seen recently, across topics and practice sessions."""
        with self._session() as conn:
            rows = conn.execute(
                "SELECT fingerprint FROM ai_question_history WHERE kind='question' ORDER BY created_at DESC LIMIT ?",
                (max(1, min(int(limit), 100000)),),
            ).fetchall()
        return {row[0] for row in rows}


    def question_seen(self, text: str) -> bool:
        """Check the permanent exact-question ledger, not just recent sessions."""
        key = fingerprint(str(text or "").strip())
        with self._session() as conn:
            row = conn.execute(
                "SELECT 1 FROM ai_question_history WHERE fingerprint=? AND kind='question' LIMIT 1",
                (key,),
            ).fetchone()
        return row is not None

    def recent_archetypes(self, topic: str, limit: int = 8) -> set[str]:
        if not topic:
            return set()
        cutoff = time.time() - self.max_age_seconds
        with self._session() as conn:
            rows = conn.execute(
                "SELECT archetype FROM ai_question_history WHERE kind='question' AND topic=? AND created_at>=? AND archetype<>'' ORDER BY created_at DESC LIMIT ?",
                (topic, cutoff, max(1, min(int(limit), 100))),
            ).fetchall()
        return {row[0] for row in rows}

    def recent_structures(self, topic: str, limit: int = 10) -> set[str]:
        """Structures used recently for a topic, to avoid number-swapped clones."""
        if not topic:
            return set()
        cutoff = time.time() - self.max_age_seconds
        with self._session() as conn:
            rows = conn.execute(
                "SELECT structure_fingerprint FROM ai_question_history WHERE kind='question' AND topic=? AND created_at>=? AND structure_fingerprint<>'' ORDER BY created_at DESC LIMIT ?",
                (topic, cutoff, max(1, min(int(limit), 100))),
            ).fetchall()
        return {row[0] for row in rows}

    def recent_variations(self, topic: str, limit: int = 10) -> set[str]:
        if not topic:
            return set()
        cutoff = time.time() - self.max_age_seconds
        with self._session() as conn:
            rows = conn.execute(
                "SELECT variation_key FROM ai_question_history WHERE kind='question' AND topic=? AND created_at>=? AND variation_key<>'' ORDER BY created_at DESC LIMIT ?",
                (topic, cutoff, max(1, min(int(limit), 100))),
            ).fetchall()
        return {row[0] for row in rows}

    def record_question(self, q: dict) -> None:
        text = str(q.get("question", "")).strip()
        if not text:
            return
        key = fingerprint(text)
        now = time.time()
        with self._session() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO ai_question_history(fingerprint,topic,grade,difficulty,structure_fingerprint,variation_key,archetype,kind,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (key, str(q.get("topic", "")), int(q.get("grade", 0) or 0), str(q.get("difficulty", "")), str(q.get("structure_fingerprint", "")), str(q.get("variation_key", "")), str(q.get("archetype", "")), "question", now),
            )

    def problem_seen(self, text: str) -> bool:
        key = fingerprint("problem|" + text)
        with self._session() as conn:
            row = conn.execute(
                "SELECT 1 FROM ai_question_history WHERE fingerprint=? AND kind='problem' LIMIT 1",
                (key,),
            ).fetchone()
        return row is not None

    def record_problem(self, topic: str, grade: int, difficulty: str, archetype: str, text: str) -> None:
        if not text.strip():
            return
        now = time.time()
        with self._session() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO ai_question_history(fingerprint,topic,grade,difficulty,archetype,kind,created_at) VALUES(?,?,?,?,?,?,?)",
                (fingerprint("problem|" + text), topic, grade, difficulty, archetype, "problem", now),
            )
