"""Account-scoped activity journal for MATH_WEB.

These are client-reported events, NOT independently graded results. They never
award points, change progress, or certify a question. Battle matches and graded
sessions remain authoritative in their own backend tables.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Literal

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from database.database import get_connection
from .auth.routes import get_current_user

router = APIRouter(prefix="/api/activity", tags=["Learner Activity"])

EventType = Literal["question_answered", "question_skipped", "game_completed", "practice_started", "topic_opened"]


class ActivityEvent(BaseModel):
    event_id: str = Field(min_length=12, max_length=128, pattern=r"^[A-Za-z0-9_:-]+$")
    event_type: EventType
    game_id: str = Field(default="", max_length=120)
    topic: str = Field(default="", max_length=160)
    question_text: str = Field(default="", max_length=3000)
    selected_answer: str = Field(default="", max_length=1000)
    is_correct: bool | None = None
    progress: int | None = Field(default=None, ge=0, le=100)


def ensure_activity_table(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS learner_activity_events (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       event_id TEXT NOT NULL,
       event_type TEXT NOT NULL,
       game_id TEXT NOT NULL DEFAULT '',
       topic TEXT NOT NULL DEFAULT '',
       question_text TEXT NOT NULL DEFAULT '',
       selected_answer TEXT NOT NULL DEFAULT '',
       client_is_correct INTEGER,
       client_progress INTEGER,
       source TEXT NOT NULL DEFAULT 'client_unverified',
       created_at TEXT NOT NULL,
       FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
       UNIQUE(user_id, event_id)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_learner_activity_user_recent ON learner_activity_events(user_id, id DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_learner_activity_user_time ON learner_activity_events(user_id, created_at)")


@router.post("/events", status_code=201)
def record_event(event: ActivityEvent, authorization: str | None = Header(default=None)):
    user = get_current_user(authorization)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    conn = get_connection()
    try:
        ensure_activity_table(conn)
        # Reject abusive event floods. An index supports this per-user lookup.
        cutoff = (now - timedelta(minutes=1)).isoformat()
        count = conn.execute(
            "SELECT COUNT(*) FROM learner_activity_events WHERE user_id=? AND created_at>=?",
            (user["id"], cutoff),
        ).fetchone()[0]
        prior = conn.execute(
            "SELECT id FROM learner_activity_events WHERE user_id=? AND event_id=?",
            (user["id"], event.event_id),
        ).fetchone()
        if prior:
            return {"success": True, "id": prior[0], "duplicate": True, "verified": False}
        if count >= 120:
            raise HTTPException(status_code=429, detail="Quá nhiều sự kiện trong một phút.")
        conn.execute("""INSERT OR IGNORE INTO learner_activity_events(
            user_id,event_id,event_type,game_id,topic,question_text,selected_answer,
            client_is_correct,client_progress,source,created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,'client_unverified',?)""", (
            user["id"], event.event_id, event.event_type, event.game_id.strip(),
            event.topic.strip(), event.question_text.strip(), event.selected_answer.strip(),
            None if event.is_correct is None else int(event.is_correct), event.progress, now.isoformat(),
        ))
        row = conn.execute(
            "SELECT id FROM learner_activity_events WHERE user_id=? AND event_id=?",
            (user["id"], event.event_id),
        ).fetchone()
        conn.commit()
        return {"success": True, "id": row[0], "duplicate": False, "verified": False}
    finally:
        conn.close()
