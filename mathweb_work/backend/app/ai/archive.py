"""Persistent archive of AI-created practice questions for the admin library."""
import json
from datetime import datetime, timezone
from database.database import get_connection


def archive_questions(grade: int, topics: list[str], questions: list[dict], *, game_id: str = "", source: str = "AI runtime") -> int:
    """Store unique generated questions without interrupting the learner request."""
    if not questions:
        return 0
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    added = 0
    conn = get_connection()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS admin_question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT, grade INTEGER NOT NULL CHECK(grade BETWEEN 10 AND 12),
            topic TEXT NOT NULL, difficulty TEXT NOT NULL, question_type TEXT NOT NULL,
            question TEXT NOT NULL, choices_json TEXT NOT NULL DEFAULT '[]', correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT 'AI runtime',
            tags_json TEXT NOT NULL DEFAULT '[]', created_by INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            game_id TEXT NOT NULL DEFAULT '')""")
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(admin_question_bank)").fetchall()}
        if "game_id" not in cols:
            conn.execute("ALTER TABLE admin_question_bank ADD COLUMN game_id TEXT NOT NULL DEFAULT ''")
        for q in questions:
            if not isinstance(q, dict):
                continue
            text = str(q.get("question") or q.get("prompt") or "").strip()
            if len(text) < 5:
                continue
            topic = str(q.get("topic") or (topics[0] if topics else "general"))[:160]
            exists = conn.execute("SELECT id FROM admin_question_bank WHERE grade=? AND lower(trim(question))=lower(trim(?)) LIMIT 1", (grade, text)).fetchone()
            if exists:
                continue
            choices = q.get("options") or q.get("statements") or q.get("choices") or []
            answer = q.get("answer", q.get("correct_answer", ""))
            explanation = q.get("solution") or q.get("explanation") or ""
            tags = ["ai-generated", "runtime-archive", topic]
            conn.execute("""INSERT INTO admin_question_bank(grade,topic,difficulty,question_type,game_id,question,choices_json,correct_answer,explanation,source,tags_json,created_by,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (grade, topic, str(q.get("difficulty", "medium")), str(q.get("question_type", "multiple_choice")), str(game_id or ""), text, json.dumps(choices, ensure_ascii=False), str(answer), str(explanation), source, json.dumps(tags, ensure_ascii=False), None, now, now))
            added += 1
        conn.commit()
        return added
    finally:
        conn.close()
