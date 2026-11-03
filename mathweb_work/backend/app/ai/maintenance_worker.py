"""Background maintenance for the MATH WEB question bank.

Runs only while the API process is alive. It expands under-covered topics with
original questions from the local question engine; it does not copy pages from
third-party websites. External-source ingestion requires separately configured,
permitted sources and is intentionally not an unrestricted web scraper.
"""
from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone

from database.database import get_connection

_worker_thread: threading.Thread | None = None
_stop_event = threading.Event()
_status_lock = threading.Lock()
_status = {"running": False, "enabled": True, "last_run": None, "last_result": "Chưa chạy", "next_run_seconds": 0}


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _get_enabled() -> bool:
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM admin_system_settings WHERE key='ai_worker_enabled'").fetchone()
        return (row["value"] if row else "1") == "1"
    except Exception:
        return True
    finally:
        conn.close()


def _set_status(**values):
    with _status_lock:
        _status.update(values)


def get_status():
    with _status_lock:
        current = dict(_status)
    current["enabled"] = _get_enabled()
    return current


def set_enabled(enabled: bool):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO admin_system_settings(key,value,updated_at) VALUES('ai_worker_enabled',?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at", ("1" if enabled else "0", _now()))
        conn.commit()
    finally:
        conn.close()
    _set_status(enabled=enabled)
    return get_status()


def run_maintenance_once(trigger="manual"):
    """Generate a small, bounded batch for the least-covered curriculum topic."""
    from app.ai.routes import service as ai_service

    _set_status(running=True, last_run=_now(), last_result=f"Đang chạy ({trigger})")
    conn = get_connection()
    added = 0
    topic_label = ""
    try:
        topics_by_grade = ai_service.topics()
        candidates = []
        counts = {}
        rows = conn.execute("SELECT grade, topic, COUNT(*) n FROM admin_question_bank GROUP BY grade, topic").fetchall()
        for row in rows:
            counts[(int(row["grade"]), str(row["topic"]).casefold())] = int(row["n"])
        for grade_text, topics in topics_by_grade.items():
            grade = int(grade_text)
            for topic in topics:
                tid = str(topic.get("id", ""))
                name = str(topic.get("name", tid))
                n = max(counts.get((grade, tid.casefold()), 0), counts.get((grade, name.casefold()), 0))
                if tid and n < 20:
                    candidates.append((n, grade, tid, name))
        if not candidates:
            result = "Ngân hàng đã đạt ngưỡng tối thiểu 20 câu/chủ đề; không cần bổ sung tự động."
            conn.execute("INSERT INTO admin_ai_jobs(status,started_at,finished_at,detail) VALUES(?,?,?,?)", ("completed", _now(), _now(), result))
            conn.commit()
            _set_status(running=False, last_result=result, next_run_seconds=21600)
            return {"success": True, "added": 0, "message": result}
        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        # Round-robin among equally sparse topics to avoid focusing on one subject.
        min_count = candidates[0][0]
        sparse = [x for x in candidates if x[0] == min_count]
        import random
        _, grade, topic_id, topic_label = random.choice(sparse)
        existing = conn.execute("SELECT lower(trim(question)) q FROM admin_question_bank WHERE grade=? AND (lower(topic)=lower(?) OR lower(topic)=lower(?))", (grade, topic_id, topic_label)).fetchall()
        existing_set = {r["q"] for r in existing}
        difficulty = "easy" if min_count < 5 else ("medium" if min_count < 12 else "hard")
        qtype = ("multiple_choice", "short_answer", "true_false")[int(time.time()) % 3]
        result = ai_service.generate_set(grade, [topic_id], 2, difficulty, qtype, history=[], game_id="")
        for q in result.get("questions", []):
            text = str(q.get("question", "")).strip()
            if not text or text.casefold() in existing_set:
                continue
            choices = q.get("options") or q.get("statements") or []
            answer = q.get("answer", "")
            explanation = q.get("solution") or q.get("explanation") or ""
            conn.execute("""INSERT INTO admin_question_bank
                (grade,topic,difficulty,question_type,game_id,question,choices_json,correct_answer,explanation,source,tags_json,created_by,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (grade, topic_id, str(q.get("difficulty", difficulty)), str(q.get("question_type", qtype)), "",
                 text, json.dumps(choices, ensure_ascii=False), str(answer), str(explanation),
                 "AI MATH_WEB Background Worker (generated locally)", json.dumps(["ai-generated", "background", topic_id], ensure_ascii=False),
                 None, _now(), _now()))
            existing_set.add(text.casefold())
            added += 1
        message = f"Đã bổ sung {added} câu cho Toán {grade}, chủ đề {topic_label}." if added else f"Chưa tạo được câu mới cho chủ đề {topic_label}; sẽ thử lại ở chu kỳ sau."
        conn.execute("INSERT INTO admin_ai_jobs(status,started_at,finished_at,detail) VALUES(?,?,?,?)", ("completed", _status.get("last_run") or _now(), _now(), message))
        conn.commit()
        _set_status(running=False, last_result=message, next_run_seconds=21600)
        return {"success": True, "added": added, "grade": grade, "topic": topic_label, "message": message}
    except Exception as exc:
        try:
            conn.execute("INSERT INTO admin_ai_jobs(status,started_at,finished_at,detail) VALUES(?,?,?,?)", ("error", _status.get("last_run") or _now(), _now(), str(exc)[:1000]))
            conn.commit()
        except Exception:
            pass
        _set_status(running=False, last_result=f"Lỗi: {exc}", next_run_seconds=21600)
        return {"success": False, "added": added, "message": str(exc)}
    finally:
        conn.close()


def _worker_loop():
    _set_status(running=False, enabled=_get_enabled(), next_run_seconds=60)
    while not _stop_event.wait(60):
        if not _get_enabled():
            _set_status(enabled=False, running=False, next_run_seconds=3600)
            continue
        _set_status(enabled=True, next_run_seconds=21600)
        # Run at most every six hours; the first pass is intentionally delayed after startup.
        last = _status.get("last_run")
        if not last:
            _set_status(next_run_seconds=21600)
            run_maintenance_once("scheduled")
            continue
        try:
            last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
        except Exception:
            elapsed = 21600
        if elapsed >= 21600:
            run_maintenance_once("scheduled")
        else:
            _set_status(next_run_seconds=max(0, int(21600 - elapsed)))


def start_worker():
    global _worker_thread
    if _worker_thread and _worker_thread.is_alive():
        return
    _stop_event.clear()
    _worker_thread = threading.Thread(target=_worker_loop, name="mathweb-ai-maintenance", daemon=True)
    _worker_thread.start()


def stop_worker():
    _stop_event.set()
