"""Administrative API for MATH WEB. All authorization is enforced server-side."""
import json
import os
import secrets
import sqlite3
import csv
import io
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from database.database import get_connection
from .auth.routes import extract_bearer_token, verify_token, hash_password, verify_password, create_admin_token
from app.ai.routes import service as ai_service
from app.ai.maintenance_worker import get_status as get_ai_worker_status, set_enabled as set_ai_worker_enabled, run_maintenance_once
from app.ai.archive import archive_questions

router = APIRouter(prefix="/api/admin", tags=["Administration"])
ADMIN_USERNAME = "admin19022011"
# No default administrator password is embedded in downloadable source code.
# On first run only, an auto-generated password is shown in the backend log
# unless the operator provided MATHWEB_BOOTSTRAP_ADMIN_PASSWORD.
BOOTSTRAP_PASSWORD = os.getenv("MATHWEB_BOOTSTRAP_ADMIN_PASSWORD")


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_admin_schema_and_account():
    conn = get_connection()
    try:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "role" not in cols: conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
        if "status" not in cols: conn.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
        if "banned_at" not in cols: conn.execute("ALTER TABLE users ADD COLUMN banned_at TEXT")
        if "ban_reason" not in cols: conn.execute("ALTER TABLE users ADD COLUMN ban_reason TEXT")
        if "auth_version" not in cols: conn.execute("ALTER TABLE users ADD COLUMN auth_version INTEGER NOT NULL DEFAULT 0")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)")
        conn.execute("""CREATE TABLE IF NOT EXISTS admin_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            auth_version INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            last_login TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS admin_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, admin_user_id INTEGER,
            action TEXT NOT NULL, target_user_id INTEGER, details TEXT, created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS admin_question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT, grade INTEGER NOT NULL CHECK(grade BETWEEN 10 AND 12),
            topic TEXT NOT NULL, difficulty TEXT NOT NULL, question_type TEXT NOT NULL,
            question TEXT NOT NULL, choices_json TEXT NOT NULL DEFAULT '[]', correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT 'Admin MATH_WEB',
            tags_json TEXT NOT NULL DEFAULT '[]', created_by INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""")
        qcols = {r["name"] for r in conn.execute("PRAGMA table_info(admin_question_bank)").fetchall()}
        if "game_id" not in qcols: conn.execute("ALTER TABLE admin_question_bank ADD COLUMN game_id TEXT NOT NULL DEFAULT ''")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_admin_questions_topic ON admin_question_bank(grade, topic, difficulty)")
        conn.execute("""CREATE TABLE IF NOT EXISTS admin_system_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)""")
        conn.execute("INSERT OR IGNORE INTO admin_system_settings(key,value,updated_at) VALUES('ai_worker_enabled','1',?)", (now_iso(),))
        conn.execute("""CREATE TABLE IF NOT EXISTS admin_ai_jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, detail TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS learning_assignments (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',grade INTEGER NOT NULL,topic TEXT NOT NULL,difficulty TEXT NOT NULL DEFAULT 'medium',question_type TEXT NOT NULL DEFAULT 'mixed',question_count INTEGER NOT NULL DEFAULT 10,due_at TEXT,status TEXT NOT NULL DEFAULT 'published',created_by INTEGER,created_at TEXT NOT NULL,updated_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS learning_assignment_targets (id INTEGER PRIMARY KEY AUTOINCREMENT,assignment_id INTEGER NOT NULL,user_id INTEGER NOT NULL,status TEXT NOT NULL DEFAULT 'assigned',questions_json TEXT NOT NULL DEFAULT '[]',started_at TEXT,submitted_at TEXT,score REAL,correct_count INTEGER,elapsed_seconds INTEGER,answer_json TEXT NOT NULL DEFAULT '{}',feedback_json TEXT NOT NULL DEFAULT '{}',UNIQUE(assignment_id,user_id),FOREIGN KEY(assignment_id) REFERENCES learning_assignments(id) ON DELETE CASCADE,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_assignment_targets_user ON learning_assignment_targets(user_id,status)")
        conn.execute("""CREATE TABLE IF NOT EXISTS learner_personalization (
            user_id INTEGER PRIMARY KEY, preferred_difficulty TEXT NOT NULL DEFAULT 'auto',
            difficulty_adjustment INTEGER NOT NULL DEFAULT 0 CHECK(difficulty_adjustment BETWEEN -1 AND 1),
            source_mode TEXT NOT NULL DEFAULT 'mixed', question_count_scale REAL NOT NULL DEFAULT 1.0,
            teacher_note TEXT NOT NULL DEFAULT '', updated_by INTEGER, updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)""")
        defaults = {
            'question_sources': '["AI runtime", "MATHWEB_KNOWLEDGE_LIBRARY", "admin_question_bank"]',
            'distribution_rules': '{"practice":"mixed","homework":"library_then_ai","battle":"ai","review":"adaptive"}',
            'default_difficulty': 'trung cấp', 'xp_multiplier': '1.0', 'daily_streak_goal': '1'
        }
        for key, value in defaults.items():
            conn.execute("INSERT OR IGNORE INTO admin_system_settings(key,value,updated_at) VALUES(?,?,?)", (key,value,now_iso()))
        conn.execute("""CREATE TABLE IF NOT EXISTS learner_streaks (
            user_id INTEGER PRIMARY KEY, current_streak INTEGER NOT NULL DEFAULT 0,
            longest_streak INTEGER NOT NULL DEFAULT 0, last_activity_date TEXT,
            updated_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)""")

        # Migrate an earlier build's admin row to the independent admin_accounts table once.
        admin = conn.execute("SELECT id, username, password_hash, status, created_at FROM users WHERE username=? LIMIT 1", (ADMIN_USERNAME,)).fetchone()
        existing = conn.execute("SELECT id FROM admin_accounts WHERE username=? LIMIT 1", (ADMIN_USERNAME,)).fetchone()
        if not existing:
            if admin:
                conn.execute("INSERT INTO admin_accounts(username,password_hash,status,auth_version,created_at) VALUES(?,?,?,?,?)",
                             (ADMIN_USERNAME, admin["password_hash"], "active", 0, admin["created_at"] or now_iso()))
            else:
                initial_password = BOOTSTRAP_PASSWORD or secrets.token_urlsafe(24)
                if len(initial_password) < 8:
                    raise RuntimeError("MATHWEB_BOOTSTRAP_ADMIN_PASSWORD must contain at least 8 characters.")
                conn.execute("INSERT INTO admin_accounts(username,password_hash,status,auth_version,created_at) VALUES(?,?,?,?,?)",
                             (ADMIN_USERNAME, hash_password(initial_password), "active", 0, now_iso()))
                # Only printed for newly created admins, not on every restart.
                print("[MATH_WEB ADMIN SETUP] Initial username:", ADMIN_USERNAME, flush=True)
                print("[MATH_WEB ADMIN SETUP] Initial password:", initial_password, flush=True)
                print("[MATH_WEB ADMIN SETUP] Change this password immediately after signing in.", flush=True)
        # Keep old audit/user references safe, but hide the legacy shadow from learner lists.
        conn.execute("DROP INDEX IF EXISTS idx_single_admin_role")
        if admin:
            conn.execute("UPDATE users SET username=?, role='user', status='banned', ban_reason='Tài khoản quản trị đã được chuyển sang kho admin_accounts.', auth_version=auth_version+1 WHERE id=?",
                         (f"legacy_admin_archived_{admin['id']}", admin["id"]))
        conn.execute("UPDATE users SET role='user' WHERE role='admin'")
        conn.commit()
    finally:
        conn.close()


ensure_admin_schema_and_account()


def require_admin(authorization: str | None):
    token = extract_bearer_token(authorization)
    payload = verify_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Cần đăng nhập bằng tài khoản quản trị riêng.")
    conn = get_connection()
    try:
        row = conn.execute("SELECT id, username, status, auth_version FROM admin_accounts WHERE id=?", (payload["user_id"],)).fetchone()
        if not row or row["username"] != payload.get("admin_username"):
            raise HTTPException(status_code=403, detail="Phiên quản trị không hợp lệ.")
        if row["status"] != "active":
            raise HTTPException(status_code=403, detail="Tài khoản quản trị không hoạt động.")
        if int(row["auth_version"] or 0) != int(payload.get("auth_version", 0)):
            raise HTTPException(status_code=401, detail="Phiên quản trị đã bị thu hồi.")
        return row
    finally:
        conn.close()


def audit(conn, admin_id: int, action: str, target_id: int | None = None, details: Any = None):
    conn.execute("INSERT INTO admin_audit_logs(admin_user_id, action, target_user_id, details, created_at) VALUES (?, ?, ?, ?, ?)",
                 (admin_id, action, target_id, json.dumps(details, ensure_ascii=False) if details is not None else None, now_iso()))


class BanRequest(BaseModel):
    reason: str = Field(default="Vi phạm quy định sử dụng", min_length=3, max_length=500)

class ResetPasswordRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

class AdminQuestionRequest(BaseModel):
    grade: int = Field(ge=10, le=12)
    topic: str = Field(min_length=1, max_length=160)
    difficulty: str = Field(default="trung cấp", max_length=40)
    question_type: str = Field(default="multiple_choice", max_length=40)
    game_id: str = Field(default="", max_length=100)
    question: str = Field(min_length=5, max_length=10000)
    choices: list[Any] = Field(default_factory=list, max_length=12)
    correct_answer: str = Field(min_length=1, max_length=2000)
    explanation: str = Field(default="", max_length=10000)
    source: str = Field(default="Admin MATH_WEB", max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=30)


@router.get("/me")
def admin_me(authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    return {"username": admin["username"], "role": "admin", "status": admin["status"]}


@router.get("/dashboard")
def dashboard(authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        user_stats = conn.execute("""SELECT COUNT(*) total,
            SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) active,
            SUM(CASE WHEN status='banned' THEN 1 ELSE 0 END) banned,
            SUM(CASE WHEN role='admin' THEN 1 ELSE 0 END) admins,
            SUM(CASE WHEN date(created_at)=date('now') THEN 1 ELSE 0 END) created_today
            FROM users WHERE username NOT LIKE 'legacy_admin_archived_%' AND username NOT LIKE 'trial_%'""").fetchone()
        game_stats = conn.execute("""SELECT COUNT(*) games, COALESCE(SUM(total_questions),0) attempts,
            COALESCE(SUM(correct),0) correct, COALESCE(SUM(wrong),0) wrong,
            COALESCE(AVG(CASE WHEN total_questions>0 THEN 100.0*correct/total_questions END),0) avg_accuracy
            FROM game_results gr JOIN users u ON u.id=gr.user_id WHERE u.username NOT LIKE 'trial_%'""").fetchone()
        recent_users = conn.execute("SELECT id, username, player_id, status, role, created_at, last_seen FROM users WHERE username NOT LIKE 'legacy_admin_archived_%' AND username NOT LIKE 'trial_%' ORDER BY id DESC LIMIT 8").fetchall()
        recent_games = conn.execute("""SELECT gr.id, u.username, gr.game_name, gr.topic, gr.total_questions,
            gr.correct, gr.wrong, gr.score, gr.created_at FROM game_results gr JOIN users u ON u.id=gr.user_id WHERE u.username NOT LIKE 'trial_%'
            ORDER BY gr.id DESC LIMIT 10""").fetchall()
        question_count = conn.execute("SELECT COUNT(*) FROM admin_question_bank").fetchone()[0]
        user_summary = dict(user_stats)
        user_summary["admins"] = conn.execute("SELECT COUNT(*) FROM admin_accounts WHERE status='active'").fetchone()[0]
        return {"users": user_summary, "learning": dict(game_stats), "admin_questions": question_count,
                "recent_users": [dict(r) for r in recent_users], "recent_games": [dict(r) for r in recent_games]}
    finally:
        conn.close()


@router.get("/users")
def list_users(authorization: str | None = Header(default=None), q: str = Query(default="", max_length=100),
              status: str = Query(default="all", pattern="^(all|active|banned)$"),
              limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    require_admin(authorization)
    conn = get_connection()
    try:
        where, params = ["username NOT LIKE 'legacy_admin_archived_%'", "username NOT LIKE 'trial_%'"], []
        if q.strip():
            like = f"%{q.strip()}%"
            where.append("(username LIKE ? OR player_id LIKE ? OR CAST(id AS TEXT) LIKE ?)")
            params.extend([like, like, like])
        if status != "all":
            where.append("status=?"); params.append(status)
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        total = conn.execute("SELECT COUNT(*) FROM users" + clause, params).fetchone()[0]
        rows = conn.execute("""SELECT id, player_id, username, role, status, ban_reason, banned_at,
            level, xp, total_games, total_correct, total_wrong, total_blank, total_score, last_seen, created_at
            FROM users""" + clause + " ORDER BY id DESC LIMIT ? OFFSET ?", params + [limit, offset]).fetchall()
        return {"total": total, "limit": limit, "offset": offset, "users": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.get("/users/{user_id}")
def user_detail(user_id: int, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        user = conn.execute("""SELECT id, player_id, username, role, status, ban_reason, banned_at, level, xp,
            total_games, total_correct, total_wrong, total_blank, total_score, last_seen, created_at
            FROM users WHERE id=? AND username NOT LIKE 'trial_%' AND username NOT LIKE 'legacy_admin_archived_%'""", (user_id,)).fetchone()
        if not user: raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
        games = conn.execute("""SELECT id, game_id, game_name, topic, total_questions, correct, wrong, blank, score, xp, created_at
            FROM game_results WHERE user_id=? ORDER BY id DESC LIMIT 50""", (user_id,)).fetchall()
        topic_stats = conn.execute("""SELECT topic, COUNT(*) sessions, COALESCE(SUM(total_questions),0) questions,
            COALESCE(SUM(correct),0) correct, COALESCE(SUM(wrong),0) wrong,
            ROUND(AVG(CASE WHEN total_questions>0 THEN 100.0*correct/total_questions END),1) accuracy
            FROM game_results WHERE user_id=? GROUP BY topic ORDER BY sessions DESC LIMIT 30""", (user_id,)).fetchall()
        session_rows = conn.execute("""SELECT id, game_id, topic, difficulty, concept, question_json, correct_answer,
            selected_answer, is_correct, status, created_at, answered_at
            FROM question_sessions WHERE user_id=? ORDER BY id DESC LIMIT 50""", (user_id,)).fetchall()
        sessions = []
        for session in session_rows:
            item = dict(session)
            raw_question = item.pop("question_json", None)
            try:
                parsed = json.loads(raw_question) if raw_question else {}
                item["question_text"] = parsed.get("question", "") if isinstance(parsed, dict) else str(parsed)
            except Exception:
                item["question_text"] = str(raw_question or "")
            sessions.append(item)
        audit(conn, admin["id"], "view_user_learning_data", user_id, {"scope": "account_and_learning_summary"})
        conn.commit()
        return {"user": dict(user), "recent_games": [dict(r) for r in games],
                "topic_stats": [dict(r) for r in topic_stats], "recent_question_sessions": sessions}
    finally:
        conn.close()


@router.post("/users/{user_id}/ban")
def ban_user(user_id: int, data: BanRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        target = conn.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,)).fetchone()
        if not target: raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
        if target["username"] == ADMIN_USERNAME or target["role"] == "admin":
            raise HTTPException(status_code=400, detail="Không thể cấm tài khoản quản trị duy nhất.")
        conn.execute("UPDATE users SET status='banned', banned_at=?, ban_reason=? WHERE id=?", (now_iso(), data.reason.strip(), user_id))
        audit(conn, admin["id"], "ban_user", user_id, {"username": target["username"], "reason": data.reason.strip()})
        conn.commit()
        return {"success": True, "message": f"Đã cấm tài khoản {target['username']}."}
    finally: conn.close()


@router.post("/users/{user_id}/unban")
def unban_user(user_id: int, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        target = conn.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,)).fetchone()
        if not target: raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
        if target["username"] == ADMIN_USERNAME or target["role"] == "admin":
            raise HTTPException(status_code=400, detail="Không thể thay đổi trạng thái quản trị.")
        conn.execute("UPDATE users SET status='active', banned_at=NULL, ban_reason=NULL WHERE id=?", (user_id,))
        audit(conn, admin["id"], "unban_user", user_id, {"username": target["username"]})
        conn.commit()
        return {"success": True, "message": f"Đã mở cấm tài khoản {target['username']}."}
    finally: conn.close()


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: int, data: ResetPasswordRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        target = conn.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,)).fetchone()
        if not target: raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
        if target["username"] == ADMIN_USERNAME or target["role"] == "admin":
            raise HTTPException(status_code=400, detail="Không dùng chức năng này để đổi mật khẩu admin. Hãy dùng mục Đổi mật khẩu.")
        conn.execute("UPDATE users SET password_hash=?, auth_version=auth_version+1 WHERE id=?", (hash_password(data.password), user_id))
        audit(conn, admin["id"], "reset_user_password", user_id, {"username": target["username"]})
        conn.commit()
        return {"success": True, "message": "Đã đặt lại mật khẩu. Hãy gửi mật khẩu mới cho người dùng qua kênh riêng an toàn."}
    finally: conn.close()


@router.post("/change-password")
def change_admin_password(data: ChangePasswordRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        row = conn.execute("SELECT password_hash, auth_version FROM admin_accounts WHERE id=?", (admin["id"],)).fetchone()
        if not row or not verify_password(data.current_password, row["password_hash"]):
            raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")
        new_version = int(row["auth_version"] or 0) + 1
        conn.execute("UPDATE admin_accounts SET password_hash=?, auth_version=? WHERE id=?", (hash_password(data.new_password), new_version, admin["id"]))
        audit(conn, admin["id"], "change_admin_password")
        conn.commit()
        token = create_admin_token(admin["id"], admin["username"], new_version)
        return {"success": True, "message": "Đã đổi mật khẩu quản trị.", "token": token}
    finally: conn.close()


@router.get("/questions")
def list_admin_questions(authorization: str | None = Header(default=None), q: str = Query(default="", max_length=160),
                        grade: int | None = Query(default=None, ge=10, le=12), topic: str = Query(default="", max_length=160),
                        game_id: str = Query(default="", max_length=100), limit: int = Query(default=100, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    require_admin(authorization)
    conn = get_connection()
    try:
        clauses, params = [], []
        if q.strip():
            like = f"%{q.strip()}%"; clauses.append("(topic LIKE ? OR question LIKE ? OR source LIKE ?)"); params += [like, like, like]
        if grade is not None: clauses.append("grade=?"); params.append(grade)
        if topic.strip(): clauses.append("lower(topic)=lower(?)"); params.append(topic.strip())
        if game_id.strip(): clauses.append("lower(game_id)=lower(?)"); params.append(game_id.strip())
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        total = conn.execute("SELECT COUNT(*) FROM admin_question_bank" + where, params).fetchone()[0]
        rows = conn.execute("SELECT * FROM admin_question_bank" + where + " ORDER BY id DESC LIMIT ? OFFSET ?", params + [limit, offset]).fetchall()
        items = []
        for row in rows:
            item = dict(row); item["choices"] = json.loads(item.pop("choices_json") or "[]"); item["tags"] = json.loads(item.pop("tags_json") or "[]"); items.append(item)
        return {"total": total, "questions": items}
    finally: conn.close()


@router.post("/questions")
def add_admin_question(data: AdminQuestionRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        conn.execute("""INSERT INTO admin_question_bank
            (grade, topic, difficulty, question_type, game_id, question, choices_json, correct_answer, explanation, source, tags_json, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.grade, data.topic.strip(), data.difficulty.strip(), data.question_type.strip(), data.game_id.strip(), data.question.strip(),
             json.dumps(data.choices, ensure_ascii=False), data.correct_answer.strip(), data.explanation.strip(), data.source.strip(),
             json.dumps(data.tags, ensure_ascii=False), admin["id"], now_iso(), now_iso()))
        question_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        audit(conn, admin["id"], "add_question", None, {"question_id": question_id, "grade": data.grade, "topic": data.topic})
        conn.commit()
        return {"success": True, "id": question_id, "message": "Đã thêm câu hỏi vào ngân hàng quản trị."}
    finally: conn.close()


@router.put("/questions/{question_id}")
def update_admin_question(question_id: int, data: AdminQuestionRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        row = conn.execute("SELECT id FROM admin_question_bank WHERE id=?", (question_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")
        conn.execute("""UPDATE admin_question_bank SET grade=?, topic=?, difficulty=?, question_type=?, game_id=?,
            question=?, choices_json=?, correct_answer=?, explanation=?, source=?, tags_json=?, updated_at=? WHERE id=?""",
            (data.grade, data.topic.strip(), data.difficulty.strip(), data.question_type.strip(), data.game_id.strip(),
             data.question.strip(), json.dumps(data.choices, ensure_ascii=False), data.correct_answer.strip(),
             data.explanation.strip(), data.source.strip(), json.dumps(data.tags, ensure_ascii=False), now_iso(), question_id))
        audit(conn, admin["id"], "edit_question", None, {"question_id": question_id, "grade": data.grade, "topic": data.topic})
        conn.commit()
        return {"success": True, "id": question_id, "message": "Đã cập nhật câu hỏi trong ngân hàng."}
    finally:
        conn.close()


@router.delete("/questions/{question_id}")
def delete_admin_question(question_id: int, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        row = conn.execute("SELECT id, topic FROM admin_question_bank WHERE id=?", (question_id,)).fetchone()
        if not row: raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")
        conn.execute("DELETE FROM admin_question_bank WHERE id=?", (question_id,))
        audit(conn, admin["id"], "delete_question", None, {"question_id": question_id, "topic": row["topic"]})
        conn.commit()
        return {"success": True, "message": "Đã xóa câu hỏi khỏi ngân hàng quản trị."}
    finally: conn.close()


@router.get("/library/topics")
def admin_library_topics(authorization: str | None = Header(default=None)):
    """Return the exact topic catalogue used by the learner-facing AI engine."""
    require_admin(authorization)
    conn = get_connection()
    try:
        counts = {}
        for row in conn.execute("SELECT grade, topic, COUNT(*) AS n FROM admin_question_bank GROUP BY grade, topic"):
            counts[(int(row["grade"]), str(row["topic"]).casefold())] = int(row["n"])
        result = []
        catalogue = ai_service.topics()
        for grade_text, topics in catalogue.items():
            grade = int(grade_text)
            for topic in topics:
                topic_id = str(topic.get("id", ""))
                name = str(topic.get("name", topic_id))
                result.append({**topic, "grade": grade, "bank_count": max(counts.get((grade, topic_id.casefold()), 0), counts.get((grade, name.casefold()), 0))})
        return {"total_topics": len(result), "topics": result}
    finally:
        conn.close()


@router.get("/library/overview")
def admin_library_overview(authorization: str | None = Header(default=None)):
    require_admin(authorization)
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM admin_question_bank").fetchone()[0]
        grades = conn.execute("SELECT grade, COUNT(*) AS n FROM admin_question_bank GROUP BY grade ORDER BY grade").fetchall()
        by_type = conn.execute("SELECT question_type, COUNT(*) AS n FROM admin_question_bank GROUP BY question_type").fetchall()
        by_source = conn.execute("SELECT source, COUNT(*) AS n FROM admin_question_bank GROUP BY source ORDER BY n DESC LIMIT 10").fetchall()
        return {"total_questions": total, "by_grade": [dict(x) for x in grades], "by_type": [dict(x) for x in by_type], "top_sources": [dict(x) for x in by_source], "worker": get_ai_worker_status()}
    finally:
        conn.close()


def _load_game_catalogue():
    """Read generated game pages' exact MATH_GAME metadata; fall back to manifest entries."""
    root = Path(__file__).resolve().parents[2]
    games = []
    seen_paths = set()
    for path in (root / "games" / "knowledge").rglob("*.html"):
        try:
            html = path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"window\.MATH_GAME\s*=\s*(\{.*?\})\s*;", html, re.S)
            if not match: continue
            meta = json.loads(match.group(1))
            title = str(meta.get("title") or path.stem).strip()
            topic_id = str(meta.get("knowledgeId") or meta.get("topicId") or "").strip()
            topic_name = str(meta.get("topic") or "").strip()
            grade = int(meta.get("grade") or 10)
            gid = f"{topic_id}_{title}" if topic_id else title
            rel = path.relative_to(root).as_posix()
            games.append({"game_id": gid, "name": title, "grade": grade, "topic_id": topic_id, "topic_name": topic_name, "path": rel, "icon": "🎮"})
            seen_paths.add(rel)
        except Exception:
            continue
    manifest_path = root / "games" / "individual-games-manifest.json"
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict): continue
                rel = str(item.get("path") or "")
                if rel in seen_paths: continue
                name = str(item.get("game") or item.get("name") or rel).strip()
                topic_id = str(item.get("knowledge_id") or item.get("topic_id") or "").strip()
                topic_name = str(item.get("knowledge") or item.get("topic_name") or "").strip()
                grade = int(item.get("grade") or 10)
                gid = str(item.get("game_id") or item.get("id") or (f"{topic_id}_{name}" if topic_id else name)).strip()
                games.append({"game_id": gid, "name": name, "grade": grade, "topic_id": topic_id, "topic_name": topic_name, "path": rel, "icon": str(item.get("icon") or "🎮")})
    except Exception:
        pass
    return games


@router.get("/library/hierarchy")
def admin_library_hierarchy(authorization: str | None = Header(default=None)):
    """A unified topic -> game -> curated question hierarchy for the admin workspace."""
    require_admin(authorization)
    conn = get_connection()
    try:
        topic_catalogue = ai_service.topics()
        game_rows = _load_game_catalogue()
        topics_out = []
        for grade_text, items in topic_catalogue.items():
            grade = int(grade_text)
            for item in items:
                tid = str(item.get("id") or "")
                name = str(item.get("name") or tid)
                game_list = [g for g in game_rows if g["grade"] == grade and (g["topic_id"].casefold() == tid.casefold() or g["topic_name"].casefold() == name.casefold())]
                count = conn.execute("SELECT COUNT(*) FROM admin_question_bank WHERE grade=? AND (lower(topic)=lower(?) OR lower(topic)=lower(?))", (grade, tid, name)).fetchone()[0]
                topics_out.append({**item, "grade": grade, "id": tid, "name": name, "question_count": int(count), "game_count": len(game_list), "games": game_list})
        return {"total_topics": len(topics_out), "total_games": len(game_rows), "topics": topics_out}
    finally:
        conn.close()


class QuestionFileImportRequest(BaseModel):
    filename: str = Field(default="upload.txt", max_length=255)
    content: str = Field(min_length=1, max_length=3_000_000)
    content_encoding: str = Field(default="text", pattern="^(text|base64)$")
    grade: int = Field(default=10, ge=10, le=12)
    default_topic: str = Field(default="", max_length=160)
    default_game_id: str = Field(default="", max_length=200)
    dry_run: bool = False


def _norm_import_key(value):
    value = str(value or "").strip().casefold().replace("đ", "d")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def _import_value(row, *keys, default=""):
    if not isinstance(row, dict):
        return default
    normalized = {_norm_import_key(k): v for k, v in row.items()}
    for key in keys:
        value = normalized.get(_norm_import_key(key))
        if value is not None and str(value).strip() != "":
            return value
    return default


def _parse_question_upload(filename, content, content_encoding="text"):
    suffix = Path(filename or "upload.txt").suffix.casefold()
    if content_encoding == "base64":
        import base64
        try:
            raw_bytes = base64.b64decode(content, validate=True)
        except Exception as exc:
            raise ValueError("Dữ liệu tệp nhị phân không hợp lệ.") from exc
        if len(raw_bytes) > 2_000_000:
            raise ValueError("Tệp sau giải mã vượt quá 2 MB.")
        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(raw_bytes))
                content = "\n".join(page.extract_text() or "" for page in reader.pages)
            except ImportError as exc:
                raise ValueError("Thiếu thư viện pypdf. Chạy pip install -r requirements.txt trong thư mục backend.") from exc
            except Exception as exc:
                raise ValueError(f"Không trích xuất được văn bản PDF (PDF scan cần OCR riêng): {exc}") from exc
        elif suffix == ".docx":
            try:
                from docx import Document
                document = Document(io.BytesIO(raw_bytes))
                lines = [p.text for p in document.paragraphs if p.text.strip()]
                for table in document.tables:
                    for row in table.rows:
                        lines.append(" | ".join(cell.text.strip() for cell in row.cells))
                content = "\n".join(lines)
            except ImportError as exc:
                raise ValueError("Thiếu thư viện python-docx. Chạy pip install -r requirements.txt trong thư mục backend.") from exc
            except Exception as exc:
                raise ValueError(f"Không đọc được tài liệu DOCX: {exc}") from exc
        elif suffix == ".xlsx":
            try:
                from openpyxl import load_workbook
                workbook = load_workbook(io.BytesIO(raw_bytes), read_only=True, data_only=True)
                sheet = workbook.active
                values = list(sheet.values)
                if not values:
                    return []
                headers = [str(v or "").strip() for v in values[0]]
                return [dict(zip(headers, row)) for row in values[1:] if any(v is not None for v in row)]
            except ImportError as exc:
                raise ValueError("Thiếu thư viện openpyxl. Chạy pip install -r requirements.txt trong thư mục backend.") from exc
            except Exception as exc:
                raise ValueError(f"Không đọc được bảng XLSX: {exc}") from exc
        else:
            raise ValueError("Tệp base64 chỉ hỗ trợ PDF, DOCX hoặc XLSX.")
    if suffix == ".json" or content.lstrip().startswith(("[", "{")):
        data = json.loads(content)
        if isinstance(data, dict):
            data = data.get("questions") or data.get("items") or data.get("data") or [data]
        if not isinstance(data, list):
            raise ValueError("JSON cần là một danh sách câu hỏi hoặc có trường questions/items.")
        return [x for x in data if isinstance(x, dict)]
    if suffix == ".csv":
        return list(csv.DictReader(io.StringIO(content)))
    # Text/Markdown format: each block begins with Question/Câu hỏi; metadata can be key: value lines.
    blocks = re.split(r"(?im)^\s*(?:câu\s*hỏi|câu|bài|question|problem)\s*\d*\s*[:.)-]\s*", content)
    if len(blocks) <= 1:
        raise ValueError("Không nhận diện được câu hỏi. Dùng JSON, CSV hoặc TXT/MD theo mẫu Câu hỏi 1: ...; Đáp án: ...; Chủ đề: ...")
    rows = []
    for block in blocks[1:]:
        row = {}
        current = None
        body = []
        choices = []
        for line in block.splitlines():
            m = re.match(r"\s*(chủ đề|topic|game|game_id|độ khó|difficulty|loại câu hỏi|question_type|đáp án|answer|lời giải|explanation|giải thích|lựa chọn|choices)\s*[:：]\s*(.*)", line, re.I)
            if m:
                key = _norm_import_key(m.group(1))
                if key in {"chu_de", "topic"}: key = "topic"
                elif key in {"game", "game_id"}: key = "game_id"
                elif key in {"do_kho", "difficulty"}: key = "difficulty"
                elif key in {"loai_cau_hoi", "question_type"}: key = "question_type"
                elif key in {"dap_an", "answer"}: key = "correct_answer"
                elif key in {"loi_giai", "explanation", "giai_thich"}: key = "explanation"
                elif key in {"lua_chon", "choices"}: key = "choices"
                row[key] = m.group(2).strip(); current = key
            elif current == "choices" and line.strip():
                row[current] = str(row.get(current, "")) + "\n" + line.strip()
            elif re.match(r"^\s*[A-D][).:]\s+", line, re.I):
                choices.append(re.sub(r"^\s*[A-D][).:]\s+", "", line, flags=re.I).strip())
            else:
                body.append(line)
        row["question"] = "\n".join(body).strip()
        if choices and "choices" not in row:
            row["choices"] = choices
        rows.append(row)
    return rows


def _plain_text(value):
    value = str(value or "").casefold().replace("đ", "d")
    value = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def _resolve_topic_for_import(raw_topic, grade, catalogue, default_topic, content_hint=""):
    entries = catalogue.get(str(grade), [])
    query = str(raw_topic or default_topic or "").strip()
    if query:
        for item in entries:
            if _plain_text(query) in {_plain_text(item.get("id", "")), _plain_text(item.get("name", ""))}:
                return item
        # Fuzzy resolution only when there is a strong match; uncertain assignments are sent for review.
        scored = []
        for item in entries:
            for label in (item.get("id", ""), item.get("name", "")):
                score = SequenceMatcher(None, _plain_text(query), _plain_text(label)).ratio()
                if score >= 0.86:
                    scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        if scored and (len(scored) == 1 or scored[0][0] > scored[1][0] + 0.04):
            return scored[0][1]
        # A provided but ambiguous topic should not be overridden by guessing from question text.
        return None
    # Smart content routing for files without an explicit topic field: match topic names and declared subtopics.
    text = _plain_text(content_hint)
    if not text:
        return None
    scored = []
    for item in entries:
        score = 0.0
        name = _plain_text(item.get("name", ""))
        topic_id = _plain_text(item.get("id", "")).replace("_", " ")
        if name and name in text: score += 5.0 + min(len(name) / 20, 2)
        if topic_id and topic_id in text: score += 3.0
        for sub in item.get("subtopics", []) or []:
            term = _plain_text(sub)
            if len(term) >= 4 and term in text: score += 1.5
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored and scored[0][0] >= 1.5 and (len(scored) == 1 or scored[0][0] >= scored[1][0] + 0.75):
        return scored[0][1]
    return None


@router.post("/questions/import-file")
def import_questions_from_file(data: QuestionFileImportRequest, authorization: str | None = Header(default=None)):
    """Review structured question files and route questions to matching topic/game IDs."""
    admin = require_admin(authorization)
    try:
        rows = _parse_question_upload(data.filename, data.content, data.content_encoding)
    except (ValueError, json.JSONDecodeError, csv.Error) as exc:
        raise HTTPException(status_code=422, detail=f"Không đọc được tệp câu hỏi: {exc}")
    if len(rows) > 2000:
        raise HTTPException(status_code=413, detail="Mỗi lần nhập tối đa 2.000 câu hỏi.")
    catalogue = ai_service.topics()
    game_lookup = {}
    for item in _load_game_catalogue():
        gid = str(item.get("game_id") or "").strip()
        game_name = str(item.get("name") or gid).strip()
        for alias in (gid, game_name, item.get("path")):
            if alias: game_lookup[str(alias).strip().casefold()] = {"id": gid, "name": game_name, "topic_id": str(item.get("topic_id") or ""), "grade": int(item.get("grade") or 10)}
    conn = get_connection()
    added, skipped, review = 0, 0, []
    try:
        for index, row in enumerate(rows, 1):
            qtext = str(_import_value(row, "question", "câu hỏi", "prompt", "content", "đề bài")).strip()
            answer = str(_import_value(row, "correct_answer", "answer", "đáp án", "đáp án đúng", "solution_answer")).strip()
            grade_raw = _import_value(row, "grade", "khối", "khối lớp", default=data.grade)
            try: grade = int(grade_raw)
            except (TypeError, ValueError): grade = data.grade
            if grade not in (10, 11, 12): grade = data.grade
            topic_raw = _import_value(row, "topic", "chủ đề", "knowledge", "knowledge_id", default=data.default_topic)
            game_raw = str(_import_value(row, "game_id", "game", "trò chơi", default=data.default_game_id)).strip()
            explanation_hint = str(_import_value(row, "explanation", "lời giải", "giải thích", "solution", default=""))
            topic = _resolve_topic_for_import(topic_raw, grade, catalogue, data.default_topic, qtext + " " + explanation_hint)
            game = game_lookup.get(game_raw.casefold()) if game_raw else None
            if game and game.get("grade") != grade:
                game = None
            if not topic and game:
                topic = _resolve_topic_for_import(game.get("topic_id"), grade, catalogue, "")
            if topic and not game and not game_raw:
                # When the file identifies a topic but not a game, route by difficulty to the topic's matching game tier.
                candidates = [g for g in _load_game_catalogue() if int(g.get("grade") or 10) == grade and str(g.get("topic_id") or "").casefold() == str(topic.get("id") or "").casefold()]
                difficulty_hint = _plain_text(_import_value(row, "difficulty", "độ khó", default="trung cấp"))
                preferred = "kham pha" if any(k in difficulty_hint for k in ("easy", "foundation", "nen tang")) else "trum cuoi" if any(k in difficulty_hint for k in ("hard", "advanced", "nang cao", "expert")) else "nhiem vu"
                game = next((g for g in candidates if preferred in _plain_text(g.get("name", ""))), candidates[0] if candidates else None)
            if not qtext or not answer or not topic:
                skipped += 1
                review.append({"row": index, "question": qtext[:180], "reason": "Thiếu nội dung/đáp án hoặc chưa xác định chắc chắn được chủ đề", "topic_detected": topic_raw, "game_detected": game_raw})
                continue
            topic_id = str(topic.get("id"))
            game_id = game["id"] if game else (data.default_game_id.strip() or "")
            choices_raw = _import_value(row, "choices", "options", "lựa chọn", "đáp án lựa chọn", default=[])
            if isinstance(choices_raw, str):
                try: choices = json.loads(choices_raw) if choices_raw.strip().startswith("[") else [x.strip() for x in choices_raw.splitlines() if x.strip()]
                except Exception: choices = [x.strip() for x in choices_raw.splitlines() if x.strip()]
            elif isinstance(choices_raw, list): choices = choices_raw
            else: choices = []
            difficulty = str(_import_value(row, "difficulty", "độ khó", default="trung cấp")).strip()
            qtype = str(_import_value(row, "question_type", "loại câu hỏi", "type", default="multiple_choice")).strip()
            explanation = str(_import_value(row, "explanation", "lời giải", "giải thích", "solution", default="")).strip()
            duplicate = conn.execute("SELECT id FROM admin_question_bank WHERE grade=? AND lower(trim(question))=lower(trim(?)) LIMIT 1", (grade, qtext)).fetchone()
            if duplicate:
                skipped += 1
                continue
            if not data.dry_run:
                conn.execute("""INSERT INTO admin_question_bank (grade,topic,difficulty,question_type,game_id,question,choices_json,correct_answer,explanation,source,tags_json,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (grade, topic_id, difficulty, qtype, game_id, qtext, json.dumps(choices, ensure_ascii=False), answer, explanation, f"Upload AI review · {data.filename}", json.dumps(["file-import", "ai-topic-routed", topic_id], ensure_ascii=False), admin["id"], now_iso(), now_iso()))
            added += 1
        if not data.dry_run:
            audit(conn, admin["id"], "import_questions_file", None, {"filename": data.filename, "added": added, "skipped": skipped, "needs_review": len(review)})
            conn.commit()
        return {"success": True, "dry_run": data.dry_run, "parsed": len(rows), "added": added, "skipped": skipped, "needs_review": review[:200], "message": ("Đã phân tích thử, chưa lưu câu hỏi." if data.dry_run else f"Đã nhập {added} câu hỏi; bỏ qua {skipped} câu trùng/không đủ dữ kiện.")}
    finally:
        conn.close()


class GenerateBankRequest(BaseModel):
    grade: int = Field(ge=10, le=12)
    topic: str = Field(min_length=1, max_length=160)
    difficulty: str = Field(default="medium", max_length=40)
    question_type: str = Field(default="multiple_choice", max_length=40)
    count: int = Field(default=5, ge=1, le=20)


@router.post("/questions/generate")
def generate_bank_questions(data: GenerateBankRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    catalogue = ai_service.topics(data.grade)
    topic_item = next((x for x in catalogue if str(x.get("id", "")).casefold() == data.topic.casefold() or str(x.get("name", "")).casefold() == data.topic.casefold()), None)
    if not topic_item:
        raise HTTPException(status_code=400, detail="Chủ đề không thuộc thư viện kiến thức của khối đã chọn.")
    topic_id = str(topic_item["id"])
    try:
        generated = ai_service.generate_set(data.grade, [topic_id], data.count, data.difficulty, data.question_type, history=[], game_id="")
        try: archive_questions(data.grade, [topic_id], generated.get("questions", []), source="AI runtime · admin generated")
        except Exception: pass
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=f"AI chưa tạo được bộ câu hỏi hợp lệ: {exc}")
    conn = get_connection()
    try:
        added = 0
        skipped = 0
        for question in generated.get("questions", []):
            text = str(question.get("question", "")).strip()
            if not text:
                skipped += 1
                continue
            duplicate = conn.execute("SELECT id FROM admin_question_bank WHERE grade=? AND lower(trim(question))=lower(trim(?)) LIMIT 1", (data.grade, text)).fetchone()
            if duplicate:
                skipped += 1
                continue
            choices = question.get("options") or question.get("statements") or []
            answer = question.get("answer", "")
            explanation = question.get("solution") or question.get("explanation") or ""
            conn.execute("""INSERT INTO admin_question_bank
                (grade,topic,difficulty,question_type,game_id,question,choices_json,correct_answer,explanation,source,tags_json,created_by,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (data.grade, topic_id, str(question.get("difficulty", data.difficulty)), str(question.get("question_type", data.question_type)), "", text,
                 json.dumps(choices, ensure_ascii=False), str(answer), str(explanation), "AI MATH_WEB · Admin generated",
                 json.dumps(["ai-generated", "admin-reviewed-required", topic_id], ensure_ascii=False), admin["id"], now_iso(), now_iso()))
            added += 1
        audit(conn, admin["id"], "generate_bank_questions", None, {"grade": data.grade, "topic": topic_id, "added": added, "skipped": skipped})
        conn.commit()
        return {"success": True, "added": added, "skipped_duplicates_or_invalid": skipped, "message": f"Đã lưu {added} câu hỏi vào ngân hàng. Nên rà soát lời giải trước khi xuất bản cho người học."}
    finally:
        conn.close()


@router.get("/ai-worker/status")
def ai_worker_status(authorization: str | None = Header(default=None)):
    require_admin(authorization)
    return get_ai_worker_status()


class AIWorkerToggleRequest(BaseModel):
    enabled: bool


@router.post("/ai-worker/toggle")
def ai_worker_toggle(data: AIWorkerToggleRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    status = set_ai_worker_enabled(data.enabled)
    conn = get_connection()
    try:
        audit(conn, admin["id"], "toggle_ai_worker", None, {"enabled": data.enabled})
        conn.commit()
    finally:
        conn.close()
    return {"success": True, "worker": status, "message": "Đã bật tác vụ AI nền." if data.enabled else "Đã tắt tác vụ AI nền."}


@router.post("/ai-worker/run-once")
def ai_worker_run_once(authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    result = run_maintenance_once("admin")
    conn = get_connection()
    try:
        audit(conn, admin["id"], "run_ai_worker_once", None, result)
        conn.commit()
    finally:
        conn.close()
    return result


@router.get("/ai-worker/jobs")
def ai_worker_jobs(authorization: str | None = Header(default=None), limit: int = Query(default=50, ge=1, le=200)):
    require_admin(authorization)
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id,status,started_at,finished_at,detail FROM admin_ai_jobs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return {"jobs": [dict(r) for r in rows]}
    finally:
        conn.close()



class AssignmentCreateRequest(BaseModel):
    title: str = Field(min_length=3,max_length=180)
    description: str = Field(default="",max_length=3000)
    grade: int = Field(ge=10,le=12)
    topic: str = Field(min_length=1,max_length=160)
    difficulty: str = Field(default="medium",max_length=40)
    question_type: str = Field(default="mixed",max_length=40)
    question_count: int = Field(default=10,ge=1,le=30)
    due_at: str | None = Field(default=None,max_length=40)
    student_ids: list[int] = Field(default_factory=list,max_length=500)

class AssignmentSubmitRequest(BaseModel):
    answers: dict[str,Any] = Field(default_factory=dict)
    reasoning: dict[str,str] = Field(default_factory=dict)
    elapsed_seconds: int = Field(ge=0,le=86400)

def _student_id(authorization):
    payload=verify_token(extract_bearer_token(authorization))
    if not payload or payload.get("role")=="admin": raise HTTPException(status_code=401,detail="Cần đăng nhập bằng tài khoản học sinh.")
    conn=get_connection()
    try:
        row=conn.execute("SELECT status,auth_version FROM users WHERE id=?",(payload.get("user_id"),)).fetchone()
        if not row or row["status"]!="active": raise HTTPException(status_code=403,detail="Tài khoản không hoạt động.")
        if int(row["auth_version"] or 0) != int(payload.get("auth_version",0)):
            raise HTTPException(status_code=401,detail="Phiên đăng nhập đã hết hiệu lực. Vui lòng đăng nhập lại.")
        return int(payload["user_id"])
    finally: conn.close()

@router.get("/learning/overview")
def learning_overview(authorization: str | None = Header(default=None)):
    admin=require_admin(authorization);conn=get_connection()
    try:
        learners=conn.execute("""SELECT u.id,u.username,u.player_id,u.level,u.total_games,u.total_correct,u.total_wrong,u.total_blank,u.last_seen,COALESCE(ROUND(100.0*u.total_correct/NULLIF(u.total_correct+u.total_wrong+u.total_blank,0),1),0) accuracy,(SELECT COUNT(*) FROM learning_assignment_targets t WHERE t.user_id=u.id AND t.status='submitted') assignments_done,(SELECT COUNT(*) FROM learning_assignment_targets t WHERE t.user_id=u.id AND t.status IN ('assigned','in_progress')) assignments_pending FROM users u WHERE u.status='active' AND u.username NOT LIKE 'legacy_admin_archived_%' AND u.username NOT LIKE 'trial_%' ORDER BY u.last_seen DESC LIMIT 300""").fetchall()
        topics=conn.execute("""SELECT u.id user_id,u.username,gr.topic,COUNT(*) sessions,SUM(gr.total_questions) questions,SUM(gr.correct) correct,SUM(gr.wrong) wrong,ROUND(100.0*SUM(gr.correct)/NULLIF(SUM(gr.total_questions),0),1) accuracy FROM game_results gr JOIN users u ON u.id=gr.user_id WHERE u.username NOT LIKE 'trial_%' GROUP BY u.id,gr.topic HAVING questions>0 ORDER BY accuracy ASC LIMIT 250""").fetchall()
        assignments=conn.execute("""SELECT a.*,COUNT(t.id) assigned_count,SUM(CASE WHEN t.status='submitted' THEN 1 ELSE 0 END) submitted_count,ROUND(AVG(t.score),1) avg_score FROM learning_assignments a LEFT JOIN learning_assignment_targets t ON t.assignment_id=a.id GROUP BY a.id ORDER BY a.id DESC LIMIT 100""").fetchall()
        totals={"learners":len(learners),"assignments":conn.execute("SELECT COUNT(*) FROM learning_assignments").fetchone()[0],"pending":conn.execute("SELECT COUNT(*) FROM learning_assignment_targets WHERE status IN ('assigned','in_progress')").fetchone()[0],"submitted":conn.execute("SELECT COUNT(*) FROM learning_assignment_targets WHERE status='submitted'").fetchone()[0]}
        audit(conn,admin['id'],'view_learning_overview',None,{"scope":"personalization_and_assignments"});conn.commit()
        return {"totals":totals,"learners":[dict(r) for r in learners],"topic_insights":[dict(r) for r in topics],"assignments":[dict(r) for r in assignments]}
    finally: conn.close()

@router.post("/learning/assignments")
def create_learning_assignment(data:AssignmentCreateRequest,authorization: str | None = Header(default=None)):
    admin=require_admin(authorization);topic=data.topic.strip()
    item=next((x for x in ai_service.topics(data.grade) if str(x.get('id','')).casefold()==topic.casefold() or str(x.get('name','')).casefold()==topic.casefold()),None)
    if not item: raise HTTPException(status_code=400,detail="Chủ đề không thuộc thư viện của khối đã chọn.")
    conn=get_connection()
    try:
        if data.student_ids:
            marks=','.join('?' for _ in data.student_ids);rows=conn.execute(f"SELECT id FROM users WHERE id IN ({marks}) AND status='active' AND username NOT LIKE 'legacy_admin_archived_%' AND username NOT LIKE 'trial_%'",data.student_ids).fetchall();ids=sorted({int(r['id']) for r in rows})
        else: ids=[int(r['id']) for r in conn.execute("SELECT id FROM users WHERE status='active' AND username NOT LIKE 'legacy_admin_archived_%' AND username NOT LIKE 'trial_%'").fetchall()]
        if not ids: raise HTTPException(status_code=400,detail="Không có học sinh hoạt động để giao bài.")
        cur=conn.execute("INSERT INTO learning_assignments(title,description,grade,topic,difficulty,question_type,question_count,due_at,status,created_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(data.title.strip(),data.description.strip(),data.grade,str(item['id']),data.difficulty,data.question_type,data.question_count,data.due_at,'published',admin['id'],now_iso(),now_iso()))
        aid=cur.lastrowid;conn.executemany("INSERT INTO learning_assignment_targets(assignment_id,user_id) VALUES(?,?)",[(aid,i) for i in ids]);audit(conn,admin['id'],'create_learning_assignment',None,{"assignment_id":aid,"target_count":len(ids)});conn.commit()
        return {"success":True,"id":aid,"assigned_count":len(ids),"message":f"Đã giao bài cho {len(ids)} học sinh."}
    finally: conn.close()

@router.get("/learning/assignments")
def list_learning_assignments(authorization: str | None = Header(default=None)):
    require_admin(authorization);conn=get_connection()
    try:
        rows=conn.execute("SELECT a.*,COUNT(t.id) assigned_count,SUM(CASE WHEN t.status='submitted' THEN 1 ELSE 0 END) submitted_count,ROUND(AVG(t.score),1) avg_score FROM learning_assignments a LEFT JOIN learning_assignment_targets t ON t.assignment_id=a.id GROUP BY a.id ORDER BY a.id DESC LIMIT 200").fetchall();return {"assignments":[dict(r) for r in rows]}
    finally: conn.close()

@router.get("/learning/assignments/{assignment_id}/results")
def assignment_results(assignment_id:int,authorization: str | None = Header(default=None)):
    require_admin(authorization);conn=get_connection()
    try:
        rows=conn.execute("SELECT t.user_id,u.username,u.player_id,t.status,t.started_at,t.submitted_at,t.score,t.correct_count,t.elapsed_seconds,t.answer_json,t.feedback_json FROM learning_assignment_targets t JOIN users u ON u.id=t.user_id WHERE t.assignment_id=? ORDER BY u.username",(assignment_id,)).fetchall();return {"results":[dict(r) for r in rows]}
    finally: conn.close()

@router.get("/learning/path")
def personalized_learning_path(authorization: str | None = Header(default=None)):
    uid=_student_id(authorization);conn=get_connection()
    try:
        topics=conn.execute("SELECT topic,COUNT(*) sessions,SUM(total_questions) questions,SUM(correct) correct,SUM(wrong) wrong,ROUND(100.0*SUM(correct)/NULLIF(SUM(total_questions),0),1) accuracy,MAX(created_at) last_practice FROM game_results WHERE user_id=? GROUP BY topic ORDER BY accuracy ASC,sessions DESC LIMIT 50",(uid,)).fetchall()
        assignments=conn.execute("SELECT a.id,a.title,a.description,a.grade,a.topic,a.difficulty,a.question_type,a.question_count,a.due_at,t.status,t.score,t.correct_count,t.elapsed_seconds,t.submitted_at FROM learning_assignment_targets t JOIN learning_assignments a ON a.id=t.assignment_id WHERE t.user_id=? ORDER BY CASE t.status WHEN 'assigned' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END,a.id DESC LIMIT 50",(uid,)).fetchall()
        weak=[dict(t) for t in topics if t['accuracy'] is not None and t['accuracy']<70];strong=[dict(t) for t in topics if t['accuracy'] is not None and t['accuracy']>=85];recs=[]
        for t in weak[:3]: recs.append({"kind":"review","topic":t['topic'],"title":"Củng cố nền tảng: "+str(t['topic']),"reason":f"Độ chính xác {t['accuracy']}%; ôn lý thuyết và làm bài nền tảng trước khi tăng độ khó."})
        for t in strong[:2]: recs.append({"kind":"challenge","topic":t['topic'],"title":"Thử thách nâng cao: "+str(t['topic']),"reason":f"Bạn đạt {t['accuracy']}%; hãy thử bài vận dụng nhiều bước."})
        if not recs: recs=[{"kind":"start","topic":"","title":"Bắt đầu hành trình Toán","reason":"Luyện một bộ câu hỏi ngắn để hệ thống có dữ liệu cá nhân hóa."}]
        return {"topics":[dict(t) for t in topics],"weak_topics":weak,"strength_topics":strong,"recommendations":recs,"assignments":[dict(a) for a in assignments]}
    finally: conn.close()

@router.get("/learning/assignments/mine")
def my_learning_assignments(authorization: str | None = Header(default=None)):
    uid=_student_id(authorization);conn=get_connection()
    try:
        rows=conn.execute("SELECT a.id,a.title,a.description,a.grade,a.topic,a.difficulty,a.question_type,a.question_count,a.due_at,t.status,t.score,t.correct_count,t.elapsed_seconds,t.submitted_at FROM learning_assignment_targets t JOIN learning_assignments a ON a.id=t.assignment_id WHERE t.user_id=? AND a.status='published' ORDER BY CASE t.status WHEN 'assigned' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END,a.id DESC",(uid,)).fetchall();return {"assignments":[dict(r) for r in rows]}
    finally: conn.close()

@router.post("/learning/assignments/{assignment_id}/start")
def start_my_assignment(assignment_id:int,authorization: str | None = Header(default=None)):
    uid=_student_id(authorization);conn=get_connection()
    try:
        t=conn.execute("SELECT t.*,a.grade,a.topic,a.difficulty,a.question_type,a.question_count,a.title FROM learning_assignment_targets t JOIN learning_assignments a ON a.id=t.assignment_id WHERE t.assignment_id=? AND t.user_id=? AND a.status='published'",(assignment_id,uid)).fetchone()
        if not t: raise HTTPException(status_code=404,detail="Không tìm thấy bài được giao.")
        if t['status']=='submitted': raise HTTPException(status_code=409,detail="Bài này đã nộp.")
        qs=json.loads(t['questions_json'] or '[]')
        if not qs:
            profile=conn.execute("SELECT preferred_difficulty,difficulty_adjustment,source_mode,question_count_scale FROM learner_personalization WHERE user_id=?",(uid,)).fetchone()
            difficulty=str(t['difficulty']); count=int(t['question_count'])
            bank_difficulty={'easy':'nền tảng','medium':'trung cấp','hard':'nâng cao','expert':'nâng cao'}.get(difficulty,difficulty)
            if profile:
                if profile['preferred_difficulty'] and profile['preferred_difficulty']!='auto': difficulty=profile['preferred_difficulty']
                else:
                    levels=['nền tảng','trung cấp','nâng cao']
                    if difficulty in levels: difficulty=levels[max(0,min(2,levels.index(difficulty)+int(profile['difficulty_adjustment'] or 0)))]
                count=max(1,min(30,round(count*float(profile['question_count_scale'] or 1.0))))
            source_mode=profile['source_mode'] if profile else 'mixed'
            try:
                source_row=conn.execute("SELECT value FROM admin_system_settings WHERE key='question_sources'").fetchone()
                enabled_sources=json.loads(source_row['value']) if source_row else ['AI runtime','MATHWEB_KNOWLEDGE_LIBRARY','admin_question_bank']
            except Exception: enabled_sources=['AI runtime','MATHWEB_KNOWLEDGE_LIBRARY','admin_question_bank']
            if not profile:
                try:
                    raw=conn.execute("SELECT value FROM admin_system_settings WHERE key='distribution_rules'").fetchone()
                    rules=json.loads(raw['value']) if raw else {}
                    homework_rule=str(rules.get('homework','mixed'))
                    if homework_rule=='library_then_ai': source_mode='mixed'
                    elif homework_rule in ('ai','library','admin_bank','mixed'): source_mode=homework_rule
                except Exception: pass
            if source_mode in ('admin_bank','mixed','library') and 'admin_question_bank' in enabled_sources:
                rows=conn.execute("SELECT * FROM admin_question_bank WHERE grade=? AND (lower(topic)=lower(?) OR lower(topic)=lower(?)) AND (difficulty=? OR ?='auto') ORDER BY RANDOM() LIMIT ?",(int(t['grade']),str(t['topic']),str(t['topic']),bank_difficulty,bank_difficulty,count)).fetchall()
                for r in rows:
                    try: choices=json.loads(r['choices_json'] or '[]')
                    except Exception: choices=[]
                    qs.append({'question':r['question'],'options':choices,'answer':r['correct_answer'],'correct_answer':r['correct_answer'],'solution':r['explanation'],'question_type':r['question_type'],'difficulty':r['difficulty'],'source':r['source']})
            if not qs and source_mode!='admin_bank' and any(x in enabled_sources for x in ('AI runtime','MATHWEB_KNOWLEDGE_LIBRARY')):
                ai_difficulty={'nền tảng':'easy','trung cấp':'medium','nâng cao':'hard'}.get(str(difficulty).casefold(),difficulty)
                try: result=ai_service.generate_set(int(t['grade']),[str(t['topic'])],count,ai_difficulty,str(t['question_type']),history=[],game_id='')
                except Exception as e: raise HTTPException(status_code=422,detail=f"AI chưa tạo được câu hỏi: {e}")
                qs=result.get('questions',[])
            if not qs: raise HTTPException(status_code=422,detail="Chưa có câu hỏi phù hợp trong nguồn đã chọn; hãy bổ sung ngân hàng hoặc dùng nguồn AI.")
            try: archive_questions(int(t['grade']), [str(t['topic'])], qs, source=f"assigned homework · {source_mode}")
            except Exception: pass
            conn.execute("UPDATE learning_assignment_targets SET questions_json=?,started_at=?,status='in_progress' WHERE id=?",(json.dumps(qs,ensure_ascii=False),now_iso(),t['id']));conn.commit()
        safe=[{"id":str(i),"question":q.get('question',''),"options":q.get('options') or q.get('statements') or q.get('choices') or [],"question_type":q.get('question_type',t['question_type']),"difficulty":q.get('difficulty',t['difficulty'])} for i,q in enumerate(qs)]
        return {"assignment_id":assignment_id,"title":t['title'],"questions":safe,"started_at":t['started_at'] or now_iso()}
    finally: conn.close()

@router.post("/learning/assignments/{assignment_id}/submit")
def submit_my_assignment(assignment_id:int,data:AssignmentSubmitRequest,authorization: str | None = Header(default=None)):
    uid=_student_id(authorization);conn=get_connection()
    try:
        t=conn.execute("SELECT * FROM learning_assignment_targets WHERE assignment_id=? AND user_id=?",(assignment_id,uid)).fetchone()
        if not t: raise HTTPException(status_code=404,detail="Không tìm thấy bài tập.")
        if t['status']=='submitted': raise HTTPException(status_code=409,detail="Bài đã được nộp.")
        qs=json.loads(t['questions_json'] or '[]')
        if not qs: raise HTTPException(status_code=409,detail="Hãy bắt đầu làm bài trước khi nộp.")
        from .questions.answer_checker import grade_answer
        out=[];correct=0
        for i,q in enumerate(qs):
            ans=data.answers.get(str(i), '')
            expected=q.get('answer', q.get('correct_answer'))
            options=q.get('options') or q.get('statements') or q.get('choices') or []
            kind=q.get('question_type') or ('multiple_choice' if options else 'short_answer')
            question={**q,'question_type':kind,'options':options}
            ok=bool(str(ans).strip()) and grade_answer(question,ans,expected)
            correct+=int(ok)
            out.append({'id':str(i),'question':q.get('question',''),'answer':ans,
                        'correct_answer':expected,'is_correct':ok,
                        'explanation':q.get('solution') or q.get('explanation') or ''})
        score=round(100*correct/max(1,len(qs)),1);feedback={"results":out,"message":"Hoàn thành tốt!" if score>=85 else "Hãy xem lời giải và củng cố phần còn yếu." if score<70 else "Bạn đang tiến bộ, hãy rà soát câu sai."}
        submission={"answers":data.answers,"reasoning":data.reasoning}
        # Award homework XP exactly once; the submitted status guard above prevents replay farming.
        xp_setting=conn.execute("SELECT value FROM admin_system_settings WHERE key='xp_multiplier'").fetchone()
        try: xp_multiplier=max(0.25,min(3.0,float(xp_setting['value']))) if xp_setting else 1.0
        except Exception: xp_multiplier=1.0
        xp_earned=max(0,round((correct*10 + (5 if len(qs)>0 else 0))*xp_multiplier))
        learner=conn.execute("SELECT level,xp,total_games,total_correct,total_wrong,total_blank,total_score FROM users WHERE id=?",(uid,)).fetchone()
        old_level=int(learner['level'] or 0); new_level=old_level; new_xp=int(learner['xp'] or 0)+xp_earned; level_ups=0
        while new_level<1000 and new_xp >= 100 + new_level*50:
            new_level+=1;level_ups+=1;new_xp=0
        if new_level>=1000:new_level=1000;new_xp=0
        conn.execute("UPDATE users SET level=?,xp=?,total_games=total_games+1,total_correct=total_correct+?,total_wrong=total_wrong+?,total_blank=total_blank+?,total_score=total_score+? WHERE id=?",(new_level,new_xp,correct,max(0,len(qs)-correct-sum(1 for x in out if not x['answer'])),sum(1 for x in out if not x['answer']),int(score),uid))
        from datetime import datetime, timezone, timedelta, date
        today=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=7))).date().isoformat()
        streak=conn.execute("SELECT current_streak,longest_streak,last_activity_date FROM learner_streaks WHERE user_id=?",(uid,)).fetchone()
        if not streak: conn.execute("INSERT INTO learner_streaks(user_id,current_streak,longest_streak,last_activity_date,updated_at) VALUES(?,?,?,?,?)",(uid,1,1,today,now_iso()));streak_current=streak_longest=1
        elif streak['last_activity_date']==today: streak_current=int(streak['current_streak'] or 1);streak_longest=max(int(streak['longest_streak'] or 0),streak_current)
        else:
            yesterday=(date.fromisoformat(today)-timedelta(days=1)).isoformat();streak_current=int(streak['current_streak'] or 0)+1 if streak['last_activity_date']==yesterday else 1;streak_longest=max(int(streak['longest_streak'] or 0),streak_current)
            conn.execute("UPDATE learner_streaks SET current_streak=?,longest_streak=?,last_activity_date=?,updated_at=? WHERE user_id=?",(streak_current,streak_longest,today,now_iso(),uid))
        conn.execute("UPDATE learning_assignment_targets SET status='submitted',submitted_at=?,score=?,correct_count=?,elapsed_seconds=?,answer_json=?,feedback_json=? WHERE id=?",(now_iso(),score,correct,data.elapsed_seconds,json.dumps(submission,ensure_ascii=False),json.dumps(feedback,ensure_ascii=False),t['id']));conn.commit()
        return {"success":True,"score":score,"correct_count":correct,"total":len(qs),"elapsed_seconds":data.elapsed_seconds,"xp_earned":xp_earned,"user":{"level":new_level,"xp":new_xp,"level_ups":level_ups},"streak":{"current":streak_current,"longest":streak_longest},"feedback":feedback}
    finally: conn.close()

class LearningConfigRequest(BaseModel):
    question_sources: list[str] = Field(default_factory=lambda: ["AI runtime", "MATHWEB_KNOWLEDGE_LIBRARY", "admin_question_bank"], max_length=20)
    distribution_rules: dict[str, str] = Field(default_factory=dict)
    default_difficulty: str = Field(default="trung cấp", max_length=40)
    xp_multiplier: float = Field(default=1.0, ge=0.25, le=3.0)
    daily_streak_goal: int = Field(default=1, ge=1, le=20)

class LearnerPersonalizationRequest(BaseModel):
    preferred_difficulty: str = Field(default="auto", pattern="^(auto|nền tảng|trung cấp|nâng cao)$")
    difficulty_adjustment: int = Field(default=0, ge=-1, le=1)
    source_mode: str = Field(default="mixed", pattern="^(mixed|ai|library|admin_bank)$")
    question_count_scale: float = Field(default=1.0, ge=0.5, le=1.5)
    teacher_note: str = Field(default="", max_length=2000)

@router.get("/learning/config")
def get_learning_config(authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        values = {r["key"]: r["value"] for r in conn.execute("SELECT key,value FROM admin_system_settings")}
        def parsed(key, fallback):
            try: return json.loads(values.get(key, json.dumps(fallback)))
            except Exception: return fallback
        return {"question_sources": parsed("question_sources", ["AI runtime", "MATHWEB_KNOWLEDGE_LIBRARY", "admin_question_bank"]),
                "distribution_rules": parsed("distribution_rules", {"practice":"mixed","homework":"library_then_ai","battle":"ai","review":"adaptive"}),
                "default_difficulty": values.get("default_difficulty", "trung cấp"),
                "xp_multiplier": float(values.get("xp_multiplier", "1.0")),
                "daily_streak_goal": int(values.get("daily_streak_goal", "1"))}
    finally: conn.close()

@router.put("/learning/config")
def update_learning_config(data: LearningConfigRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        values = {"question_sources": json.dumps(data.question_sources, ensure_ascii=False),
                  "distribution_rules": json.dumps(data.distribution_rules, ensure_ascii=False),
                  "default_difficulty": data.default_difficulty,
                  "xp_multiplier": str(data.xp_multiplier), "daily_streak_goal": str(data.daily_streak_goal)}
        for key, value in values.items():
            conn.execute("INSERT INTO admin_system_settings(key,value,updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at", (key,value,now_iso()))
        audit(conn, admin["id"], "update_learning_config", None, {"sources": data.question_sources, "distribution": data.distribution_rules})
        conn.commit()
        return {"success": True, "message": "Đã lưu cấu hình nguồn dữ liệu, phân phối, độ khó và XP."}
    finally: conn.close()

@router.get("/users/{user_id}/personalization")
def get_user_personalization(user_id: int, authorization: str | None = Header(default=None)):
    require_admin(authorization)
    conn = get_connection()
    try:
        user = conn.execute("SELECT id,username,player_id FROM users WHERE id=? AND username NOT LIKE 'trial_%' AND username NOT LIKE 'legacy_admin_archived_%'", (user_id,)).fetchone()
        if not user: raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản học sinh thật.")
        row = conn.execute("SELECT * FROM learner_personalization WHERE user_id=?", (user_id,)).fetchone()
        return {"user":dict(user), "personalization":dict(row) if row else {"preferred_difficulty":"auto","difficulty_adjustment":0,"source_mode":"mixed","question_count_scale":1.0,"teacher_note":""}}
    finally: conn.close()

@router.put("/users/{user_id}/personalization")
def set_user_personalization(user_id: int, data: LearnerPersonalizationRequest, authorization: str | None = Header(default=None)):
    admin = require_admin(authorization)
    conn = get_connection()
    try:
        user = conn.execute("SELECT id,username FROM users WHERE id=? AND username NOT LIKE 'trial_%' AND username NOT LIKE 'legacy_admin_archived_%'", (user_id,)).fetchone()
        if not user: raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản học sinh thật.")
        conn.execute("""INSERT INTO learner_personalization(user_id,preferred_difficulty,difficulty_adjustment,source_mode,question_count_scale,teacher_note,updated_by,updated_at)
            VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET preferred_difficulty=excluded.preferred_difficulty,
            difficulty_adjustment=excluded.difficulty_adjustment,source_mode=excluded.source_mode,question_count_scale=excluded.question_count_scale,
            teacher_note=excluded.teacher_note,updated_by=excluded.updated_by,updated_at=excluded.updated_at""",
            (user_id,data.preferred_difficulty,data.difficulty_adjustment,data.source_mode,data.question_count_scale,data.teacher_note,admin["id"],now_iso()))
        audit(conn, admin["id"], "personalize_learner", user_id, data.model_dump() if hasattr(data,"model_dump") else data.dict())
        conn.commit()
        return {"success":True,"message":"Đã lưu hồ sơ cá nhân hóa cho học sinh."}
    finally: conn.close()

@router.get("/audit-logs")
def get_audit_logs(authorization: str | None = Header(default=None), limit: int = Query(default=100, ge=1, le=200)):
    require_admin(authorization)
    conn = get_connection()
    try:
        rows = conn.execute("""SELECT l.id, u.username AS admin_username, l.action, l.target_user_id, l.details, l.created_at
            FROM admin_audit_logs l LEFT JOIN admin_accounts u ON u.id=l.admin_user_id ORDER BY l.id DESC LIMIT ?""", (limit,)).fetchall()
        return {"logs": [dict(r) for r in rows]}
    finally: conn.close()


# Geometry attachments: separate table keeps existing question schema and legacy data intact.
class GeometryImageRequest(BaseModel):
    image_data: str = Field(min_length=30, max_length=2000000)

@router.put('/questions/{question_id}/geometry')
def save_question_geometry(question_id: int, data: GeometryImageRequest, authorization: str | None = Header(default=None)):
    import base64
    require_admin(authorization)
    if not data.image_data.startswith('data:image/png;base64,'):
        raise HTTPException(status_code=400, detail='Chỉ chấp nhận hình PNG')
    try:
        blob = base64.b64decode(data.image_data.split(',', 1)[1], validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail='PNG không hợp lệ')
    if len(blob) > 1200000 or not blob.startswith(b'\x89PNG\r\n\x1a\n'):
        raise HTTPException(status_code=400, detail='Ảnh vượt giới hạn hoặc không phải PNG')
    conn = get_connection()
    try:
        if not conn.execute('SELECT 1 FROM admin_question_bank WHERE id=?', (question_id,)).fetchone():
            raise HTTPException(status_code=404, detail='Không tìm thấy câu hỏi')
        conn.execute('CREATE TABLE IF NOT EXISTS admin_question_geometry (question_id INTEGER PRIMARY KEY, png BLOB NOT NULL)')
        conn.execute('INSERT OR REPLACE INTO admin_question_geometry(question_id,png) VALUES(?,?)', (question_id, blob))
        conn.commit()
        return {'success': True, 'question_id': question_id}
    finally:
        conn.close()

@router.get('/questions/{question_id}/geometry')
def get_question_geometry_admin(question_id: int, authorization: str | None = Header(default=None)):
    from fastapi.responses import Response
    require_admin(authorization)
    conn = get_connection()
    try:
        conn.execute('CREATE TABLE IF NOT EXISTS admin_question_geometry (question_id INTEGER PRIMARY KEY, png BLOB NOT NULL)')
        row = conn.execute('SELECT png FROM admin_question_geometry WHERE question_id=?', (question_id,)).fetchone()
        if row is None: raise HTTPException(status_code=404, detail='Câu hỏi chưa có hình')
        return Response(content=row['png'], media_type='image/png')
    finally: conn.close()
