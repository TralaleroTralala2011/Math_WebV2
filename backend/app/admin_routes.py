"""Administrative API for MATH WEB. All authorization is enforced server-side."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from database.database import get_connection
from .auth.routes import extract_bearer_token, verify_token, hash_password, verify_password, create_admin_token
from app.ai.routes import service as ai_service
from app.ai.maintenance_worker import get_status as get_ai_worker_status, set_enabled as set_ai_worker_enabled, run_maintenance_once

router = APIRouter(prefix="/api/admin", tags=["Administration"])
ADMIN_USERNAME = "admin19022011"
BOOTSTRAP_PASSWORD = os.getenv("MATHWEB_BOOTSTRAP_ADMIN_PASSWORD", "adminsitinh")


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

        # Migrate an earlier build's admin row to the independent admin_accounts table once.
        admin = conn.execute("SELECT id, username, password_hash, status, created_at FROM users WHERE username=? LIMIT 1", (ADMIN_USERNAME,)).fetchone()
        existing = conn.execute("SELECT id FROM admin_accounts WHERE username=? LIMIT 1", (ADMIN_USERNAME,)).fetchone()
        if not existing:
            if admin:
                conn.execute("INSERT INTO admin_accounts(username,password_hash,status,auth_version,created_at) VALUES(?,?,?,?,?)",
                             (ADMIN_USERNAME, admin["password_hash"], "active", 0, admin["created_at"] or now_iso()))
            else:
                conn.execute("INSERT INTO admin_accounts(username,password_hash,status,auth_version,created_at) VALUES(?,?,?,?,?)",
                             (ADMIN_USERNAME, hash_password(BOOTSTRAP_PASSWORD), "active", 0, now_iso()))
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
            FROM users WHERE username NOT LIKE 'legacy_admin_archived_%'""").fetchone()
        game_stats = conn.execute("""SELECT COUNT(*) games, COALESCE(SUM(total_questions),0) attempts,
            COALESCE(SUM(correct),0) correct, COALESCE(SUM(wrong),0) wrong,
            COALESCE(AVG(CASE WHEN total_questions>0 THEN 100.0*correct/total_questions END),0) avg_accuracy
            FROM game_results""").fetchone()
        recent_users = conn.execute("SELECT id, username, player_id, status, role, created_at, last_seen FROM users WHERE username NOT LIKE 'legacy_admin_archived_%' ORDER BY id DESC LIMIT 8").fetchall()
        recent_games = conn.execute("""SELECT gr.id, u.username, gr.game_name, gr.topic, gr.total_questions,
            gr.correct, gr.wrong, gr.score, gr.created_at FROM game_results gr JOIN users u ON u.id=gr.user_id
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
        where, params = ["username NOT LIKE 'legacy_admin_archived_%'"], []
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
            FROM users WHERE id=?""", (user_id,)).fetchone()
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
                        grade: int | None = Query(default=None, ge=10, le=12), limit: int = Query(default=100, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    require_admin(authorization)
    conn = get_connection()
    try:
        clauses, params = [], []
        if q.strip():
            like = f"%{q.strip()}%"; clauses.append("(topic LIKE ? OR question LIKE ? OR source LIKE ?)"); params += [like, like, like]
        if grade is not None: clauses.append("grade=?"); params.append(grade)
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


@router.get("/audit-logs")
def get_audit_logs(authorization: str | None = Header(default=None), limit: int = Query(default=100, ge=1, le=200)):
    require_admin(authorization)
    conn = get_connection()
    try:
        rows = conn.execute("""SELECT l.id, u.username AS admin_username, l.action, l.target_user_id, l.details, l.created_at
            FROM admin_audit_logs l LEFT JOIN admin_accounts u ON u.id=l.admin_user_id ORDER BY l.id DESC LIMIT ?""", (limit,)).fetchall()
        return {"logs": [dict(r) for r in rows]}
    finally: conn.close()
