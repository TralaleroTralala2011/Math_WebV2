from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from ..auth.routes import get_current_user
from ..questions.session import (
    get_question_session,
    decode_question_session
)
from database.database import get_connection


router = APIRouter(
    prefix="/api/games",
    tags=["Games"]
)


# =========================================================
# CONFIG
# =========================================================

XP_PER_CORRECT = {
    "easy": 10,
    "medium": 15,
    "hard": 25
}

SCORE_PER_CORRECT = {
    "easy": 10,
    "medium": 15,
    "hard": 25
}

MAX_LEVEL = 1000

MIN_QUESTIONS_PER_GAME = 1
MAX_QUESTIONS_PER_GAME = 50

MAX_GAME_ID_LENGTH = 100
MAX_GAME_NAME_LENGTH = 200
MAX_TOPIC_LENGTH = 100
MAX_SESSION_ID_LENGTH = 100

MAX_HISTORY_LIMIT = 100


# =========================================================
# XP HELPERS
# =========================================================

def get_required_xp(level):
    """
    XP cần để lên level tiếp theo.

    Level 0 -> 100 XP
    Level 1 -> 150 XP
    Level 2 -> 200 XP
    Level 3 -> 250 XP
    ...
    """

    try:
        level = int(level or 0)

    except (
        TypeError,
        ValueError
    ):
        level = 0

    level = max(
        0,
        min(
            level,
            MAX_LEVEL
        )
    )

    return 100 + (
        level * 50
    )


def calculate_xp_percent(
    xp,
    level
):
    """
    Tính phần trăm XP trên thanh XP.
    """

    try:
        xp = int(xp or 0)

    except (
        TypeError,
        ValueError
    ):
        xp = 0

    xp = max(
        0,
        xp
    )

    required_xp = get_required_xp(
        level
    )

    if required_xp <= 0:
        return 0

    percent = (
        xp
        /
        required_xp
    ) * 100

    return round(
        max(
            0,
            min(
                percent,
                100
            )
        ),
        2
    )


def normalize_integer(
    value,
    default=0,
    minimum=0
):
    try:
        value = int(
            value
        )

    except (
        TypeError,
        ValueError
    ):
        value = default

    return max(
        minimum,
        value
    )


def process_level_up(
    old_level,
    old_xp,
    earned_xp
):
    """
    Xử lý level theo hệ thống MATH WEB.

    Khi đủ XP:
    - level +1
    - XP reset 0

    Nếu đạt MAX_LEVEL:
    - level = MAX_LEVEL
    - XP = 0
    """

    old_level = normalize_integer(
        old_level
    )

    old_xp = normalize_integer(
        old_xp
    )

    earned_xp = normalize_integer(
        earned_xp
    )

    old_level = min(
        old_level,
        MAX_LEVEL
    )

    new_level = old_level

    new_xp = (
        old_xp
        + earned_xp
    )

    level_ups = 0

    while (
        new_level < MAX_LEVEL
        and
        new_xp >= get_required_xp(
            new_level
        )
    ):

        new_level += 1

        level_ups += 1

        new_xp = 0

    if new_level >= MAX_LEVEL:

        new_level = MAX_LEVEL
        new_xp = 0

    return (
        new_level,
        new_xp,
        level_ups
    )


# =========================================================
# REQUEST MODEL
# =========================================================

class FinishGameRequest(BaseModel):

    game_id: str = Field(
        ...,
        min_length=1,
        max_length=MAX_GAME_ID_LENGTH
    )

    game_name: str = Field(
        default="Luyện tập Toán",
        min_length=1,
        max_length=MAX_GAME_NAME_LENGTH
    )

    topic: str = Field(
        ...,
        min_length=1,
        max_length=MAX_TOPIC_LENGTH
    )

    question_sessions: list[str] = Field(
        ...,
        min_length=MIN_QUESTIONS_PER_GAME,
        max_length=MAX_QUESTIONS_PER_GAME
    )


# =========================================================
# AUTH
# =========================================================

def get_user_from_token(
    authorization
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập."
        )

    user = get_current_user(
        authorization
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập không hợp lệ."
        )

    return user


# =========================================================
# VALIDATION HELPERS
# =========================================================

def normalize_text(
    value,
    field_name,
    max_length
):
    if value is None:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} không hợp lệ."
        )

    value = str(
        value
    ).strip()

    if not value:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} không được để trống."
        )

    if len(value) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} quá dài."
        )

    return value


def normalize_game_topic(
    topic
):
    topic = normalize_text(
        topic,
        "Chủ đề",
        MAX_TOPIC_LENGTH
    )

    return topic.lower()


def validate_session_id(
    session_id
):
    session_id = normalize_text(
        session_id,
        "Session ID",
        MAX_SESSION_ID_LENGTH
    )

    return session_id


# =========================================================
# CHECK SESSION
# =========================================================

def get_session_result(
    session_id,
    user_id,
    game_id
):
    """
    Lấy kết quả một question session.

    Kiểm tra:
    - session tồn tại
    - thuộc user
    - đã trả lời
    - thuộc đúng game
    - dữ liệu session hợp lệ
    """

    session_id = validate_session_id(
        session_id
    )

    row = get_question_session(
        session_id=session_id,
        user_id=user_id
    )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Không tìm thấy câu hỏi "
                + session_id
            )
        )

    if row["status"] != "answered":
        raise HTTPException(
            status_code=400,
            detail=(
                "Câu hỏi "
                + session_id
                + " chưa được trả lời."
            )
        )

    session_game_id = row["game_id"]

    if (
        session_game_id
        and
        str(session_game_id) != str(game_id)
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Câu hỏi "
                + session_id
                + " không thuộc trò chơi này."
            )
        )

    session = decode_question_session(
        row
    )

    if session is None:
        raise HTTPException(
            status_code=500,
            detail="Dữ liệu câu hỏi không hợp lệ."
        )

    return (
        row,
        session
    )


# =========================================================
# QUESTION RESULT
# =========================================================

def get_question_difficulty(
    session
):
    public_question = session.get(
        "public_question",
        {}
    )

    if not isinstance(
        public_question,
        dict
    ):
        return "easy"

    difficulty = str(
        public_question.get(
            "difficulty",
            "easy"
        )
        or "easy"
    ).strip().lower()

    if difficulty not in XP_PER_CORRECT:
        difficulty = "easy"

    return difficulty


def is_blank_answer(
    selected_answer
):
    if selected_answer is None:
        return True

    if isinstance(
        selected_answer,
        str
    ):
        return not selected_answer.strip()

    return False


# =========================================================
# BUILD GAME RESULT
# =========================================================

def calculate_game_results(
    question_sessions,
    user_id,
    game_id
):
    results = []

    correct = 0
    wrong = 0
    blank = 0

    total_score = 0
    total_xp = 0

    for session_id in question_sessions:

        row, session = get_session_result(
            session_id=session_id,
            user_id=user_id,
            game_id=game_id
        )

        is_correct = bool(
            row["is_correct"]
        )

        selected_answer = (
            row["selected_answer"]
        )

        difficulty = get_question_difficulty(
            session
        )

        if is_correct:

            correct += 1

            earned_xp = XP_PER_CORRECT[
                difficulty
            ]

            earned_score = SCORE_PER_CORRECT[
                difficulty
            ]

            total_xp += earned_xp
            total_score += earned_score

            results.append({
                "session_id": session_id,
                "correct": True,
                "difficulty": difficulty,
                "xp": earned_xp,
                "score": earned_score,
                "blank": False,
                "wrong": False
            })

            continue

        if is_blank_answer(
            selected_answer
        ):

            blank += 1

            results.append({
                "session_id": session_id,
                "correct": False,
                "difficulty": difficulty,
                "xp": 0,
                "score": 0,
                "blank": True,
                "wrong": False
            })

            continue

        wrong += 1

        results.append({
            "session_id": session_id,
            "correct": False,
            "difficulty": difficulty,
            "xp": 0,
            "score": 0,
            "blank": False,
            "wrong": True
        })

    total_questions = (
        correct
        + wrong
        + blank
    )

    return {
        "results": results,
        "total_questions": total_questions,
        "correct": correct,
        "wrong": wrong,
        "blank": blank,
        "score": total_score,
        "xp": total_xp
    }


# =========================================================
# FINISH GAME
# =========================================================

@router.post("/finish")
def finish_game(
    data: FinishGameRequest,
    authorization: str = Header(
        default=None
    )
):
    current_user = get_user_from_token(
        authorization
    )

    game_id = normalize_text(
        data.game_id,
        "Game ID",
        MAX_GAME_ID_LENGTH
    )

    game_name = normalize_text(
        data.game_name or "Luyện tập Toán",
        "Tên game",
        MAX_GAME_NAME_LENGTH
    )

    topic = normalize_game_topic(
        data.topic
    )

    if not data.question_sessions:
        raise HTTPException(
            status_code=400,
            detail="Game chưa có câu hỏi."
        )

    if len(
        data.question_sessions
    ) > MAX_QUESTIONS_PER_GAME:
        raise HTTPException(
            status_code=400,
            detail="Game có quá nhiều câu hỏi."
        )

    # =====================================================
    # NORMALIZE SESSION IDS
    # =====================================================

    normalized_sessions = []

    for session_id in data.question_sessions:

        session_id = validate_session_id(
            session_id
        )

        normalized_sessions.append(
            session_id
        )

    # =====================================================
    # KHÔNG CHO TRÙNG SESSION
    # =====================================================

    if len(
        set(normalized_sessions)
    ) != len(
        normalized_sessions
    ):
        raise HTTPException(
            status_code=400,
            detail="Game chứa câu hỏi bị trùng."
        )

    # =====================================================
    # CALCULATE RESULT
    # =====================================================

    game_result = calculate_game_results(
        question_sessions=normalized_sessions,
        user_id=current_user["id"],
        game_id=game_id
    )

    total_questions = (
        game_result["total_questions"]
    )

    correct = game_result["correct"]
    wrong = game_result["wrong"]
    blank = game_result["blank"]

    total_score = game_result["score"]
    total_xp = game_result["xp"]

    if total_questions < MIN_QUESTIONS_PER_GAME:
        raise HTTPException(
            status_code=400,
            detail="Game không có câu hỏi hợp lệ."
        )

    # =====================================================
    # DATABASE
    # =====================================================

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # TRANSACTION LOCK
        # -------------------------------------------------

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        # -------------------------------------------------
        # CHECK DUPLICATE GAME
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                total_questions,
                correct,
                wrong,
                blank,
                score,
                xp
            FROM game_results
            WHERE
                user_id = ?
                AND game_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                current_user["id"],
                game_id
            )
        )

        existing_game = cursor.fetchone()

        if existing_game:

            connection.rollback()

            raise HTTPException(
                status_code=409,
                detail=(
                    "Trò chơi này đã được "
                    "lưu kết quả trước đó."
                )
            )

        # -------------------------------------------------
        # GET USER
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                username,
                level,
                xp,
                total_games,
                total_correct,
                total_wrong,
                total_blank,
                total_score
            FROM users
            WHERE id = ?
            """,
            (
                current_user["id"],
            )
        )

        user = cursor.fetchone()

        if not user:

            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tài khoản."
            )

        # -------------------------------------------------
        # OLD XP
        # -------------------------------------------------

        old_level = normalize_integer(
            user["level"]
        )

        old_xp = normalize_integer(
            user["xp"]
        )

        # -------------------------------------------------
        # LEVEL UP
        # -------------------------------------------------

        (
            new_level,
            new_xp,
            level_ups
        ) = process_level_up(
            old_level=old_level,
            old_xp=old_xp,
            earned_xp=total_xp
        )

        # -------------------------------------------------
        # OLD STATS
        # -------------------------------------------------

        old_total_games = normalize_integer(
            user["total_games"]
        )

        old_total_correct = normalize_integer(
            user["total_correct"]
        )

        old_total_wrong = normalize_integer(
            user["total_wrong"]
        )

        old_total_blank = normalize_integer(
            user["total_blank"]
        )

        old_total_score = normalize_integer(
            user["total_score"]
        )

        # -------------------------------------------------
        # NEW STATS
        # -------------------------------------------------

        new_total_games = (
            old_total_games
            + 1
        )

        new_total_correct = (
            old_total_correct
            + correct
        )

        new_total_wrong = (
            old_total_wrong
            + wrong
        )

        new_total_blank = (
            old_total_blank
            + blank
        )

        new_total_score = (
            old_total_score
            + total_score
        )

        # -------------------------------------------------
        # UPDATE USER
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE users
            SET
                level = ?,
                xp = ?,
                total_games = ?,
                total_correct = ?,
                total_wrong = ?,
                total_blank = ?,
                total_score = ?
            WHERE id = ?
            """,
            (
                new_level,
                new_xp,
                new_total_games,
                new_total_correct,
                new_total_wrong,
                new_total_blank,
                new_total_score,
                current_user["id"]
            )
        )

        if cursor.rowcount != 1:

            connection.rollback()

            raise HTTPException(
                status_code=500,
                detail="Không thể cập nhật tài khoản."
            )

        # -------------------------------------------------
        # SAVE GAME RESULT
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO game_results (
                user_id,
                game_id,
                game_name,
                topic,
                total_questions,
                correct,
                wrong,
                blank,
                score,
                xp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user["id"],
                game_id,
                game_name,
                topic,
                total_questions,
                correct,
                wrong,
                blank,
                total_score,
                total_xp
            )
        )

        game_result_id = (
            cursor.lastrowid
        )

        # -------------------------------------------------
        # GAME COMPLETE NOTIFICATION
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO notifications (
                user_id,
                type,
                title,
                message,
                content,
                related_id,
                is_read,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                current_user["id"],
                "game_completed",
                "Hoàn thành trò chơi",
                (
                    "Bạn đã hoàn thành "
                    + game_name
                    + " và nhận "
                    + str(total_xp)
                    + " XP."
                ),
                (
                    "Bạn đã hoàn thành "
                    + game_name
                    + ". Đúng "
                    + str(correct)
                    + "/"
                    + str(total_questions)
                    + " câu."
                ),
                game_result_id,
                __import__(
                    "datetime"
                ).datetime.now(
                    __import__(
                        "datetime"
                    ).timezone.utc
                ).isoformat()
            )
        )

        # -------------------------------------------------
        # LEVEL UP NOTIFICATION
        # -------------------------------------------------

        if level_ups > 0:

            cursor.execute(
                """
                INSERT INTO notifications (
                    user_id,
                    type,
                    title,
                    message,
                    content,
                    related_id,
                    is_read,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    current_user["id"],
                    "level_up",
                    "🎉 Lên cấp!",
                    (
                        "Chúc mừng! Bạn đã đạt "
                        "Level "
                        + str(new_level)
                        + "."
                    ),
                    (
                        "Bạn vừa lên Level "
                        + str(new_level)
                        + "!"
                    ),
                    new_level,
                    __import__(
                        "datetime"
                    ).datetime.now(
                        __import__(
                            "datetime"
                        ).timezone.utc
                    ).isoformat()
                )
            )

        # -------------------------------------------------
        # COMMIT
        # -------------------------------------------------

        connection.commit()

    except HTTPException:

        connection.rollback()

        raise

    except Exception as error:

        connection.rollback()

        print(
            "FINISH GAME ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể lưu kết quả trò chơi."
        )

    finally:

        connection.close()

    # =====================================================
    # XP BAR
    # =====================================================

    required_xp = get_required_xp(
        new_level
    )

    xp_percent = calculate_xp_percent(
        xp=new_xp,
        level=new_level
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "success": True,

        "game": {
            "game_id": game_id,
            "game_name": game_name,
            "topic": topic,
            "total_questions": total_questions,
            "correct": correct,
            "wrong": wrong,
            "blank": blank,
            "score": total_score,
            "xp_earned": total_xp
        },

        "question_results": (
            game_result["results"]
        ),

        "user": {
            "level": new_level,
            "xp": new_xp,
            "required_xp": required_xp,
            "xp_percent": xp_percent
        },

        "level_up": (
            level_ups > 0
        ),

        "old_level": old_level,
        "new_level": new_level,
        "level_ups": level_ups
    }


# =========================================================
# GET GAME HISTORY
# =========================================================

@router.get("/history")
def get_game_history(
    limit: int = Query(
        default=50,
        ge=1,
        le=MAX_HISTORY_LIMIT
    ),
    authorization: str = Header(
        default=None
    )
):
    current_user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                game_id,
                game_name,
                topic,
                total_questions,
                correct,
                wrong,
                blank,
                score,
                xp,
                created_at
            FROM game_results
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                current_user["id"],
                limit
            )
        )

        rows = cursor.fetchall()

    finally:

        connection.close()

    history = []

    for row in rows:

        history.append({
            "id": row["id"],
            "game_id": row["game_id"],
            "game_name": row["game_name"],
            "topic": row["topic"],
            "total_questions": row["total_questions"],
            "correct": row["correct"],
            "wrong": row["wrong"],
            "blank": row["blank"],
            "score": row["score"],
            "xp": row["xp"],
            "created_at": row["created_at"]
        })

    return {
        "success": True,
        "history": history,
        "count": len(history)
    }


# =========================================================
# GET HISTORY BY GAME ID
# =========================================================

@router.get("/history/{game_id}")
def get_history_by_game(
    game_id: str,
    authorization: str = Header(
        default=None
    )
):
    current_user = get_user_from_token(
        authorization
    )

    game_id = normalize_text(
        game_id,
        "Game ID",
        MAX_GAME_ID_LENGTH
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                game_id,
                game_name,
                topic,
                total_questions,
                correct,
                wrong,
                blank,
                score,
                xp,
                created_at
            FROM game_results
            WHERE
                user_id = ?
                AND game_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                current_user["id"],
                game_id,
                MAX_HISTORY_LIMIT
            )
        )

        rows = cursor.fetchall()

    finally:

        connection.close()

    history = []

    for row in rows:

        history.append({
            "id": row["id"],
            "game_id": row["game_id"],
            "game_name": row["game_name"],
            "topic": row["topic"],
            "total_questions": row["total_questions"],
            "correct": row["correct"],
            "wrong": row["wrong"],
            "blank": row["blank"],
            "score": row["score"],
            "xp": row["xp"],
            "created_at": row["created_at"]
        })

    return {
        "success": True,
        "game_id": game_id,
        "history": history,
        "count": len(history)
    }


# =========================================================
# GET GAME STATISTICS
# =========================================================

@router.get("/stats")
def get_game_statistics(
    authorization: str = Header(
        default=None
    )
):
    current_user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_games,
                COALESCE(
                    SUM(total_questions),
                    0
                ) AS total_questions,
                COALESCE(
                    SUM(correct),
                    0
                ) AS total_correct,
                COALESCE(
                    SUM(wrong),
                    0
                ) AS total_wrong,
                COALESCE(
                    SUM(blank),
                    0
                ) AS total_blank,
                COALESCE(
                    SUM(score),
                    0
                ) AS total_score,
                COALESCE(
                    SUM(xp),
                    0
                ) AS total_xp
            FROM game_results
            WHERE user_id = ?
            """,
            (
                current_user["id"],
            )
        )

        stats = cursor.fetchone()

    finally:

        connection.close()

    total_games = normalize_integer(
        stats["total_games"]
    )

    total_questions = normalize_integer(
        stats["total_questions"]
    )

    total_correct = normalize_integer(
        stats["total_correct"]
    )

    total_wrong = normalize_integer(
        stats["total_wrong"]
    )

    total_blank = normalize_integer(
        stats["total_blank"]
    )

    total_score = normalize_integer(
        stats["total_score"]
    )

    total_xp = normalize_integer(
        stats["total_xp"]
    )

    if total_questions > 0:

        accuracy = round(
            (
                total_correct
                /
                total_questions
            ) * 100,
            2
        )

    else:

        accuracy = 0

    return {
        "success": True,

        "stats": {
            "total_games": total_games,
            "total_questions": total_questions,
            "total_correct": total_correct,
            "total_wrong": total_wrong,
            "total_blank": total_blank,
            "total_score": total_score,
            "total_xp": total_xp,
            "accuracy": accuracy
        }
    }


# =========================================================
# GET CURRENT XP / LEVEL
# =========================================================

@router.get("/xp")
def get_current_xp(
    authorization: str = Header(
        default=None
    )
):
    current_user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                level,
                xp
            FROM users
            WHERE id = ?
            """,
            (
                current_user["id"],
            )
        )

        user = cursor.fetchone()

    finally:

        connection.close()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản."
        )

    level = normalize_integer(
        user["level"]
    )

    level = min(
        level,
        MAX_LEVEL
    )

    xp = normalize_integer(
        user["xp"]
    )

    if level >= MAX_LEVEL:

        xp = 0

    required_xp = get_required_xp(
        level
    )

    xp_percent = calculate_xp_percent(
        xp=xp,
        level=level
    )

    return {
        "success": True,

        "level": level,

        "xp": xp,

        "required_xp": required_xp,

        "xp_percent": xp_percent,

        "max_level": MAX_LEVEL
    }