"""
MATH WEB
Question Session Manager

File:
    backend/app/questions/session.py

Nhiệm vụ:
    - Tạo phiên làm câu hỏi
    - Lưu trạng thái phiên
    - Kiểm tra đáp án
    - Lấy dữ liệu phiên công khai
    - Giải mã dữ liệu phiên
    - Kiểm tra hết hạn
    - Kết thúc / hết hạn phiên

QUAN TRỌNG:
    File này KHÔNG được import questions.routes.
    File này KHÔNG tự import chính nó.

    routes.py sẽ import các hàm từ file này.
"""

from __future__ import annotations

import copy
import json
import secrets
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# =========================================================
# CONFIG
# =========================================================

# Thời gian sống mặc định của một question session.
# Có thể thay đổi khi gọi create_question_session().
DEFAULT_SESSION_TTL = 300

# Giới hạn thời gian tối thiểu / tối đa để tránh dữ liệu lỗi.
MIN_SESSION_TTL = 5
MAX_SESSION_TTL = 86400


# =========================================================
# MEMORY STORE
# =========================================================
#
# Session câu hỏi được lưu trong bộ nhớ của backend.
#
# Ưu điểm:
#   - Không phụ thuộc schema SQLite hiện tại.
#   - Không tạo circular import.
#   - Không làm thay đổi database hiện tại.
#   - Phù hợp với question session ngắn hạn.
#
# Lưu ý:
#   Khi backend restart, các session đang tồn tại sẽ mất.
#   Đây là hành vi phù hợp với session câu hỏi tạm thời.
#

_SESSIONS: Dict[str, Dict[str, Any]] = {}

_SESSION_LOCK = threading.RLock()


# =========================================================
# TIME HELPERS
# =========================================================

def _utc_now() -> datetime:
    """
    Trả về thời gian UTC hiện tại.
    """
    return datetime.now(timezone.utc)


def _utc_timestamp() -> float:
    """
    Trả về Unix timestamp hiện tại.
    """
    return time.time()


def _timestamp_to_iso(timestamp: float) -> str:
    """
    Chuyển Unix timestamp sang ISO 8601.
    """
    return datetime.fromtimestamp(
        timestamp,
        timezone.utc
    ).isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    """
    Chuyển giá trị sang float an toàn.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# =========================================================
# GENERAL HELPERS
# =========================================================

def _generate_session_id() -> str:
    """
    Tạo ID session đủ ngẫu nhiên.

    Ví dụ:
        qs_8f4d9e...
    """
    return "qs_" + secrets.token_urlsafe(32)


def _normalize_ttl(ttl: Any) -> int:
    """
    Chuẩn hóa thời gian sống của session.
    """
    try:
        ttl = int(ttl)
    except (TypeError, ValueError):
        ttl = DEFAULT_SESSION_TTL

    if ttl < MIN_SESSION_TTL:
        ttl = MIN_SESSION_TTL

    if ttl > MAX_SESSION_TTL:
        ttl = MAX_SESSION_TTL

    return ttl


def _normalize_answer(answer: Any) -> str:
    """
    Chuẩn hóa đáp án để so sánh.

    Ví dụ:
        12       -> "12"
        " 12 "   -> "12"
        True     -> "true"
    """
    if answer is None:
        return ""

    if isinstance(answer, bool):
        return "true" if answer else "false"

    if isinstance(answer, float):
        if answer.is_integer():
            return str(int(answer))

    return str(answer).strip().lower()


def _deep_copy(value: Any) -> Any:
    """
    Copy dữ liệu để tránh code bên ngoài vô tình sửa session gốc.
    """
    return copy.deepcopy(value)


# =========================================================
# SESSION CLEANUP
# =========================================================

def _cleanup_expired_sessions() -> None:
    """
    Xóa các session đã hết hạn khỏi bộ nhớ.
    """
    now = _utc_timestamp()

    expired_ids = []

    for session_id, session in _SESSIONS.items():
        expires_at = _safe_float(
            session.get("_expires_timestamp"),
            0
        )

        if expires_at > 0 and now >= expires_at:
            expired_ids.append(session_id)

    for session_id in expired_ids:
        session = _SESSIONS.get(session_id)

        if session is not None:
            session["status"] = "expired"
            session["expired"] = True

        # Giữ session một khoảng thời gian ngắn để API
        # vẫn có thể trả về trạng thái expired.
        #
        # Không xóa ngay ở đây.


# =========================================================
# CREATE SESSION
# =========================================================

def create_question_session(
    user_id: Any = None,
    question: Any = None,
    ttl: int = DEFAULT_SESSION_TTL,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Tạo một question session.

    Có thể gọi theo dạng:

        create_question_session(
            user_id=123,
            question=question
        )

    hoặc truyền thêm:

        create_question_session(
            user_id=123,
            question=question,
            ttl=60,
            game_id="abc"
        )

    question có thể là:
        - dict
        - object
        - string
        - bất kỳ dữ liệu JSON-compatible nào
    """

    ttl = _normalize_ttl(ttl)

    now_timestamp = _utc_timestamp()
    expires_timestamp = now_timestamp + ttl

    session_id = _generate_session_id()

    # -----------------------------------------------------
    # Xử lý question
    # -----------------------------------------------------

    if isinstance(question, dict):
        question_data = _deep_copy(question)
    elif question is None:
        question_data = {}
    else:
        question_data = {
            "question": _deep_copy(question)
        }

    # -----------------------------------------------------
    # Tìm đáp án nếu question là dict
    # -----------------------------------------------------

    correct_answer = None

    if isinstance(question_data, dict):
        possible_answer_keys = (
            "correct_answer",
            "answer",
            "correctAnswer",
            "correct",
            "result"
        )

        for key in possible_answer_keys:
            if key in question_data:
                correct_answer = question_data.get(key)
                break

    # -----------------------------------------------------
    # Cho phép truyền đáp án riêng
    # -----------------------------------------------------

    if "correct_answer" in kwargs:
        correct_answer = kwargs.get("correct_answer")

    if "answer" in kwargs:
        correct_answer = kwargs.get("answer")

    # -----------------------------------------------------
    # Thông tin bổ sung
    # -----------------------------------------------------

    game_id = kwargs.get("game_id")
    topic = kwargs.get("topic")
    difficulty = kwargs.get("difficulty")
    question_id = kwargs.get("question_id")

    session = {
        "session_id": session_id,

        "user_id": user_id,

        "question": question_data,

        "status": "active",

        "answered": False,

        "correct": False,

        "selected_answer": None,

        "correct_answer": correct_answer,

        "created_at": _timestamp_to_iso(now_timestamp),

        "expires_at": _timestamp_to_iso(expires_timestamp),

        "ttl": ttl,

        "expired": False,

        "answered_at": None,

        "remaining_seconds": ttl,

        "game_id": game_id,

        "topic": topic,

        "difficulty": difficulty,

        "question_id": question_id,

        "_created_timestamp": now_timestamp,

        "_expires_timestamp": expires_timestamp
    }

    # -----------------------------------------------------
    # Lưu session
    # -----------------------------------------------------

    with _SESSION_LOCK:
        _cleanup_expired_sessions()
        _SESSIONS[session_id] = session

    return _deep_copy(session)


# =========================================================
# GET SESSION
# =========================================================

def get_question_session(
    session_id: Any
) -> Optional[Dict[str, Any]]:
    """
    Lấy question session theo ID.

    Nếu session không tồn tại:
        return None

    Nếu session hết hạn:
        cập nhật status = expired
    """

    if session_id is None:
        return None

    session_id = str(session_id).strip()

    if not session_id:
        return None

    with _SESSION_LOCK:
        session = _SESSIONS.get(session_id)

        if session is None:
            return None

        _update_session_expiration(session)

        return _deep_copy(session)


# =========================================================
# UPDATE EXPIRATION
# =========================================================

def _update_session_expiration(
    session: Dict[str, Any]
) -> None:
    """
    Cập nhật trạng thái hết hạn.
    """

    if session.get("status") != "active":
        return

    expires_timestamp = _safe_float(
        session.get("_expires_timestamp"),
        0
    )

    now = _utc_timestamp()

    remaining = max(
        0,
        int(expires_timestamp - now)
    )

    session["remaining_seconds"] = remaining

    if expires_timestamp > 0 and now >= expires_timestamp:
        session["status"] = "expired"
        session["expired"] = True

        if not session.get("answered"):
            session["answered"] = False


# =========================================================
# DECODE SESSION
# =========================================================

def decode_question_session(
    session: Any
) -> Optional[Dict[str, Any]]:
    """
    Giải mã / chuẩn hóa session.

    Hàm này hỗ trợ:

        decode_question_session(session_id)

    hoặc:

        decode_question_session(session_dict)

    hoặc JSON string.
    """

    if session is None:
        return None

    # -----------------------------------------------------
    # Session ID
    # -----------------------------------------------------

    if isinstance(session, str):

        text = session.strip()

        # Thử tìm session theo ID trước.
        stored = get_question_session(text)

        if stored is not None:
            return stored

        # Nếu không phải ID thì thử JSON.
        try:
            decoded = json.loads(text)

            if isinstance(decoded, dict):
                return _deep_copy(decoded)

        except (json.JSONDecodeError, TypeError):
            pass

        return None

    # -----------------------------------------------------
    # Dict
    # -----------------------------------------------------

    if isinstance(session, dict):

        if "session_id" in session:
            stored = get_question_session(
                session.get("session_id")
            )

            if stored is not None:
                return stored

        return _deep_copy(session)

    return None


# =========================================================
# CHECK ANSWER
# =========================================================

def check_answer(
    session_id: Any,
    answer: Any = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Kiểm tra đáp án của người chơi.

    Kết quả trả về gồm:

        correct
        selected_answer
        correct_answer
        status
        expired
        answered
        remaining_seconds
    """

    if session_id is None:
        return {
            "success": False,
            "correct": False,
            "error": "SESSION_NOT_FOUND",
            "message": "Không tìm thấy phiên câu hỏi."
        }

    session_id = str(session_id).strip()

    if not session_id:
        return {
            "success": False,
            "correct": False,
            "error": "INVALID_SESSION_ID",
            "message": "Session ID không hợp lệ."
        }

    # Hỗ trợ:
    # check_answer(session_id, answer)
    #
    # và:
    # check_answer(session_id, selected_answer=answer)

    if answer is None and "selected_answer" in kwargs:
        answer = kwargs.get("selected_answer")

    if answer is None and "user_answer" in kwargs:
        answer = kwargs.get("user_answer")

    with _SESSION_LOCK:

        session = _SESSIONS.get(session_id)

        if session is None:
            return {
                "success": False,
                "correct": False,
                "error": "SESSION_NOT_FOUND",
                "message": "Không tìm thấy phiên câu hỏi."
            }

        _update_session_expiration(session)

        # -------------------------------------------------
        # Session đã hết hạn
        # -------------------------------------------------

        if session.get("status") == "expired":
            return {
                "success": False,
                "correct": False,
                "error": "SESSION_EXPIRED",
                "message": "Phiên câu hỏi đã hết thời gian.",
                "session_id": session_id,
                "status": "expired",
                "expired": True,
                "answered": False,
                "remaining_seconds": 0
            }

        # -------------------------------------------------
        # Không cho trả lời lại
        # -------------------------------------------------

        if session.get("answered"):

            return {
                "success": False,
                "correct": bool(
                    session.get("correct", False)
                ),
                "error": "ALREADY_ANSWERED",
                "message": "Câu hỏi này đã được trả lời.",
                "session_id": session_id,
                "status": session.get("status"),
                "answered": True,
                "selected_answer": session.get(
                    "selected_answer"
                ),
                "correct_answer": session.get(
                    "correct_answer"
                )
            }

        # -------------------------------------------------
        # Lấy đáp án đúng
        # -------------------------------------------------

        correct_answer = session.get(
            "correct_answer"
        )

        # Nếu session không có answer trực tiếp,
        # thử lấy từ question.
        if correct_answer is None:

            question = session.get("question")

            if isinstance(question, dict):

                for key in (
                    "correct_answer",
                    "answer",
                    "correctAnswer",
                    "correct",
                    "result"
                ):

                    if key in question:
                        correct_answer = question.get(key)
                        break

        # -------------------------------------------------
        # So sánh
        # -------------------------------------------------

        normalized_user_answer = _normalize_answer(
            answer
        )

        normalized_correct_answer = _normalize_answer(
            correct_answer
        )

        is_correct = (
            normalized_user_answer
            == normalized_correct_answer
        )

        now = _utc_timestamp()

        session["selected_answer"] = _deep_copy(answer)

        session["answered"] = True

        session["correct"] = is_correct

        session["answered_at"] = _timestamp_to_iso(
            now
        )

        session["status"] = (
            "correct"
            if is_correct
            else "wrong"
        )

        session["remaining_seconds"] = max(
            0,
            int(
                _safe_float(
                    session.get("_expires_timestamp"),
                    now
                ) - now
            )
        )

        return {
            "success": True,

            "correct": is_correct,

            "session_id": session_id,

            "status": session.get("status"),

            "answered": True,

            "expired": False,

            "selected_answer": _deep_copy(
                answer
            ),

            "correct_answer": _deep_copy(
                correct_answer
            ),

            "remaining_seconds": session.get(
                "remaining_seconds",
                0
            )
        }


# =========================================================
# PUBLIC SESSION
# =========================================================

def get_public_session(
    session: Any
) -> Optional[Dict[str, Any]]:
    """
    Lấy thông tin session mà frontend được phép nhìn thấy.

    Không trả đáp án đúng trước khi người chơi trả lời.
    """

    decoded = decode_question_session(session)

    if decoded is None:
        return None

    public_data = _deep_copy(decoded)

    # -----------------------------------------------------
    # Không để lộ answer trong question
    # -----------------------------------------------------

    question = public_data.get("question")

    if isinstance(question, dict):

        for key in (
            "correct_answer",
            "answer",
            "correctAnswer",
            "correct",
            "result"
        ):
            question.pop(key, None)

    # -----------------------------------------------------
    # Không để lộ correct_answer khi chưa trả lời
    # -----------------------------------------------------

    if not public_data.get("answered", False):
        public_data.pop(
            "correct_answer",
            None
        )

    # -----------------------------------------------------
    # Không để lộ internal timestamps
    # -----------------------------------------------------

    public_data.pop(
        "_created_timestamp",
        None
    )

    public_data.pop(
        "_expires_timestamp",
        None
    )

    # -----------------------------------------------------
    # Cập nhật trạng thái hết hạn
    # -----------------------------------------------------

    expires_at = public_data.get(
        "expires_at"
    )

    if expires_at:
        try:
            expires_datetime = datetime.fromisoformat(
                str(expires_at).replace(
                    "Z",
                    "+00:00"
                )
            )

            now = _utc_now()

            remaining = max(
                0,
                int(
                    (
                        expires_datetime
                        - now
                    ).total_seconds()
                )
            )

            public_data[
                "remaining_seconds"
            ] = remaining

            if remaining <= 0 and public_data.get(
                "status"
            ) == "active":

                public_data["status"] = "expired"
                public_data["expired"] = True

        except (ValueError, TypeError):
            pass

    return public_data


# =========================================================
# EXPIRE SESSION
# =========================================================

def expire_question_session(
    session_id: Any
) -> Optional[Dict[str, Any]]:
    """
    Chủ động kết thúc một question session.
    """

    if session_id is None:
        return None

    session_id = str(session_id).strip()

    if not session_id:
        return None

    with _SESSION_LOCK:

        session = _SESSIONS.get(session_id)

        if session is None:
            return None

        session["status"] = "expired"

        session["expired"] = True

        session["remaining_seconds"] = 0

        return _deep_copy(session)


# =========================================================
# IS SESSION EXPIRED
# =========================================================

def is_session_expired(
    session: Any
) -> bool:
    """
    Kiểm tra session đã hết hạn hay chưa.

    Có thể truyền:
        session_id
    hoặc:
        session dict
    """

    decoded = decode_question_session(session)

    if decoded is None:
        return True

    # Nếu đã có trạng thái expired.
    if decoded.get("expired") is True:
        return True

    if decoded.get("status") == "expired":
        return True

    # Nếu đã trả lời xong thì session không còn active.
    if decoded.get("answered") is True:
        return False

    expires_timestamp = decoded.get(
        "_expires_timestamp"
    )

    if expires_timestamp is not None:

        try:
            return (
                _utc_timestamp()
                >= float(expires_timestamp)
            )

        except (TypeError, ValueError):
            pass

    expires_at = decoded.get(
        "expires_at"
    )

    if expires_at:

        try:
            expires_datetime = datetime.fromisoformat(
                str(expires_at).replace(
                    "Z",
                    "+00:00"
                )
            )

            return _utc_now() >= expires_datetime

        except (ValueError, TypeError):
            pass

    return False


# =========================================================
# OPTIONAL HELPERS
# =========================================================

def delete_question_session(
    session_id: Any
) -> bool:
    """
    Xóa hẳn session khỏi bộ nhớ.

    Hàm này không bắt buộc cho routes.py,
    nhưng hữu ích khi cần cleanup.
    """

    if session_id is None:
        return False

    session_id = str(session_id).strip()

    if not session_id:
        return False

    with _SESSION_LOCK:

        if session_id not in _SESSIONS:
            return False

        del _SESSIONS[session_id]

        return True


def clear_question_sessions() -> None:
    """
    Xóa toàn bộ question sessions.

    Chủ yếu dùng khi reset backend / test.
    """

    with _SESSION_LOCK:
        _SESSIONS.clear()


def get_active_session_count() -> int:
    """
    Trả về số session đang active.
    """

    with _SESSION_LOCK:

        count = 0

        for session in _SESSIONS.values():

            _update_session_expiration(
                session
            )

            if session.get("status") == "active":
                count += 1

        return count


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [
    "create_question_session",
    "get_question_session",
    "decode_question_session",
    "check_answer",
    "get_public_session",
    "expire_question_session",
    "is_session_expired",
    "delete_question_session",
    "clear_question_sessions",
    "get_active_session_count",
]