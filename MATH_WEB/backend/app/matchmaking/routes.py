import json
import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from ..auth.routes import get_current_user
from ..ai.routes import service as ai_service
from database.database import get_connection


router = APIRouter(
    prefix="/api/matchmaking",
    tags=["Matchmaking"]
)


# =========================================================
# CONFIG
# =========================================================

MATCH_TOTAL_QUESTIONS = 10

MATCH_QUEUE_TIMEOUT_SECONDS = 10 * 60
MATCH_INVITE_TIMEOUT_SECONDS = 10 * 60
MATCH_MAX_DURATION_SECONDS = 30 * 60

MAX_PLAYER_ID_LENGTH = 100
MAX_MATCH_ID = 2_147_483_647
MAX_TOPIC_COUNT = 5

DEFAULT_GRADE = 12
DEFAULT_DIFFICULTY = "medium"
DEFAULT_QUESTION_TYPE = "multiple_choice"

VALID_DIFFICULTIES = {
    "easy",
    "medium",
    "hard",
    "expert"
}

VALID_QUESTION_TYPES = {
    "multiple_choice",
    "short_answer",
    "true_false"
}

VALID_MATCH_STATUSES = {
    "INVITED",
    "STARTING",
    "PLAYING",
    "FINISHED",
    "CANCELLED"
}


# =========================================================
# DATABASE INIT
# =========================================================

def init_matchmaking_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matchmaking_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                grade INTEGER DEFAULT 12,
                topics TEXT DEFAULT '[]',
                difficulty TEXT DEFAULT 'medium',
                question_type TEXT DEFAULT 'multiple_choice'
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_code TEXT NOT NULL UNIQUE,

                player1_id INTEGER NOT NULL,
                player2_id INTEGER NOT NULL,

                status TEXT NOT NULL,

                questions TEXT NOT NULL,

                topics TEXT DEFAULT '[]',
                grade INTEGER DEFAULT 12,
                difficulty TEXT DEFAULT 'medium',
                question_type TEXT DEFAULT 'multiple_choice',

                player1_answers TEXT DEFAULT '{}',
                player2_answers TEXT DEFAULT '{}',

                player1_current INTEGER DEFAULT 0,
                player2_current INTEGER DEFAULT 0,

                player1_correct INTEGER DEFAULT 0,
                player1_wrong INTEGER DEFAULT 0,
                player1_blank INTEGER DEFAULT 0,
                player1_time INTEGER DEFAULT 0,

                player2_correct INTEGER DEFAULT 0,
                player2_wrong INTEGER DEFAULT 0,
                player2_blank INTEGER DEFAULT 0,
                player2_time INTEGER DEFAULT 0,

                winner_id INTEGER,

                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS match_invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        ensure_columns(
            cursor,
            "matchmaking_queue",
            {
                "grade": "INTEGER DEFAULT 12",
                "topics": "TEXT DEFAULT '[]'",
                "difficulty": "TEXT DEFAULT 'medium'",
                "question_type": "TEXT DEFAULT 'multiple_choice'"
            }
        )

        ensure_columns(
            cursor,
            "matches",
            {
                "topics": "TEXT DEFAULT '[]'",
                "grade": "INTEGER DEFAULT 12",
                "difficulty": "TEXT DEFAULT 'medium'",
                "question_type": "TEXT DEFAULT 'multiple_choice'",
                "player1_answers": "TEXT DEFAULT '{}'",
                "player2_answers": "TEXT DEFAULT '{}'",
                "player1_current": "INTEGER DEFAULT 0",
                "player2_current": "INTEGER DEFAULT 0"
            }
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_match_queue_created
            ON matchmaking_queue(created_at)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_matches_player1
            ON matches(player1_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_matches_player2
            ON matches(player2_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_matches_status
            ON matches(status)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_match_invites_receiver
            ON match_invites(receiver_id, status)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_match_invites_match
            ON match_invites(match_id)
            """
        )

        connection.commit()

    finally:
        connection.close()


def ensure_columns(cursor, table_name, columns):
    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    existing = {
        row["name"]
        for row in cursor.fetchall()
    }

    for column_name, column_definition in columns.items():
        if column_name in existing:
            continue

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_definition}
            """
        )


init_matchmaking_tables()


# =========================================================
# REQUEST MODELS
# =========================================================

class MatchSettings(BaseModel):
    grade: int = Field(
        default=DEFAULT_GRADE,
        ge=10,
        le=12
    )

    topics: list[str] = Field(
        default_factory=list,
        max_length=MAX_TOPIC_COUNT
    )

    difficulty: str = Field(
        default=DEFAULT_DIFFICULTY
    )

    question_type: str = Field(
        default=DEFAULT_QUESTION_TYPE
    )


class InviteRequest(MatchSettings):
    player_id: str = Field(
        ...,
        min_length=1,
        max_length=MAX_PLAYER_ID_LENGTH
    )


class MatchAnswerRequest(BaseModel):
    question_index: int = Field(
        ...,
        ge=0,
        le=MATCH_TOTAL_QUESTIONS - 1
    )

    answer: object = None


class MatchSkipRequest(BaseModel):
    question_index: int = Field(
        ...,
        ge=0,
        le=MATCH_TOTAL_QUESTIONS - 1
    )


# =========================================================
# HELPERS
# =========================================================

def get_user(authorization):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập."
        )

    return get_current_user(authorization)


def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def parse_iso(value):
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    except (
        ValueError,
        TypeError
    ):
        return None


def seconds_since(value):
    parsed = parse_iso(value)

    if parsed is None:
        return None

    delta = (
        datetime.now(timezone.utc)
        - parsed
    ).total_seconds()

    return max(
        0,
        int(delta)
    )


def safe_json_loads(value, default=None):
    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return value

    try:
        return json.loads(value)

    except (
        TypeError,
        ValueError,
        json.JSONDecodeError
    ):
        return default


def safe_json_dumps(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":")
    )


def validate_match_id(match_id):
    if (
        not isinstance(match_id, int)
        or match_id <= 0
        or match_id > MAX_MATCH_ID
    ):
        raise HTTPException(
            status_code=400,
            detail="Match ID không hợp lệ."
        )


def validate_player_id(player_id):
    if not isinstance(player_id, str):
        raise HTTPException(
            status_code=400,
            detail="Player ID không hợp lệ."
        )

    player_id = player_id.strip()

    if not player_id:
        raise HTTPException(
            status_code=400,
            detail="Player ID không được để trống."
        )

    if len(player_id) > MAX_PLAYER_ID_LENGTH:
        raise HTTPException(
            status_code=400,
            detail="Player ID quá dài."
        )

    return player_id


def normalize_settings(data):
    grade = int(
        getattr(
            data,
            "grade",
            DEFAULT_GRADE
        )
    )

    if grade < 10 or grade > 12:
        raise HTTPException(
            status_code=400,
            detail="Khối lớp không hợp lệ."
        )

    difficulty = str(
        getattr(
            data,
            "difficulty",
            DEFAULT_DIFFICULTY
        )
    ).strip().lower()

    if difficulty not in VALID_DIFFICULTIES:
        difficulty = DEFAULT_DIFFICULTY

    question_type = str(
        getattr(
            data,
            "question_type",
            DEFAULT_QUESTION_TYPE
        )
    ).strip().lower()

    aliases = {
        "choice": "multiple_choice",
        "mcq": "multiple_choice",
        "multiple-choice": "multiple_choice",
        "input": "short_answer",
        "short": "short_answer",
        "short-answer": "short_answer",
        "tf": "true_false",
        "true-false": "true_false"
    }

    question_type = aliases.get(
        question_type,
        question_type
    )

    if question_type not in VALID_QUESTION_TYPES:
        question_type = DEFAULT_QUESTION_TYPE

    topics = getattr(
        data,
        "topics",
        []
    )

    if not isinstance(topics, list):
        topics = []

    cleaned_topics = []

    for topic in topics:
        if not isinstance(topic, str):
            continue

        topic = topic.strip()

        if (
            topic
            and topic not in cleaned_topics
        ):
            cleaned_topics.append(topic)

    return {
        "grade": grade,
        "topics": cleaned_topics[:MAX_TOPIC_COUNT],
        "difficulty": difficulty,
        "question_type": question_type
    }


def get_default_topics(grade):
    try:
        topics = ai_service.topics(grade)

        if isinstance(topics, list):
            result = []

            for topic in topics:
                if isinstance(topic, dict):
                    topic_id = (
                        topic.get("id")
                        or topic.get("code")
                        or topic.get("topic_id")
                    )

                    if topic_id:
                        result.append(
                            str(topic_id)
                        )

                elif isinstance(topic, str):
                    result.append(topic)

            if result:
                return result[:MAX_TOPIC_COUNT]

    except Exception:
        pass

    return [
        "PROBABILITY",
        "COMBINATION",
        "PERMUTATION",
        "FUNCTION",
        "SYSTEM_EQUATION"
    ]


def normalize_topics_for_grade(grade, topics):
    if not topics:
        return get_default_topics(grade)

    try:
        normalized = ai_service.knowledge.normalize_topics(
            grade,
            topics
        )

        if normalized:
            return normalized[:MAX_TOPIC_COUNT]

    except Exception:
        pass

    valid = []

    for topic in topics:
        try:
            if ai_service.knowledge.get(topic):
                valid.append(topic)
        except Exception:
            pass

    return valid[:MAX_TOPIC_COUNT]


def get_common_topics(grade, topics1, topics2):
    normalized1 = normalize_topics_for_grade(
        grade,
        topics1
    )

    normalized2 = normalize_topics_for_grade(
        grade,
        topics2
    )

    if not normalized1 or not normalized2:
        return []

    common = []

    for topic in normalized1:
        if (
            topic in normalized2
            and topic not in common
        ):
            common.append(topic)

    return common[:MAX_TOPIC_COUNT]


def generate_ai_battle_questions(
    grade,
    topics,
    difficulty,
    question_type
):
    if not topics:
        raise HTTPException(
            status_code=409,
            detail="Hai người chơi không có chủ đề chung."
        )

    try:
        result = ai_service.generate_set(
            grade=grade,
            topics=topics,
            count=MATCH_TOTAL_QUESTIONS,
            difficulty=difficulty,
            question_type=question_type,
            history=[]
        )

    except (
        ValueError,
        RuntimeError
    ) as error:
        raise HTTPException(
            status_code=400,
            detail=f"AI không thể tạo bộ câu hỏi: {error}"
        )

    questions = result.get(
        "questions",
        []
    )

    if not isinstance(questions, list):
        raise HTTPException(
            status_code=500,
            detail="AI trả về bộ câu hỏi không hợp lệ."
        )

    if len(questions) != MATCH_TOTAL_QUESTIONS:
        raise HTTPException(
            status_code=500,
            detail="AI không tạo đủ số câu hỏi cho trận đấu."
        )

    clean_questions = []

    for index, question in enumerate(
        questions
    ):
        if not isinstance(question, dict):
            raise HTTPException(
                status_code=500,
                detail="Một câu hỏi AI không hợp lệ."
            )

        item = dict(question)

        item["battle_index"] = index

        clean_questions.append(item)

    return clean_questions


def sanitize_question(question, index=None):
    safe = {
        "id": question.get("id"),
        "battle_index": (
            question.get("battle_index")
            if index is None
            else index
        ),
        "topic": question.get("topic"),
        "type": question.get("type"),
        "question_type": question.get(
            "question_type"
        ),
        "question": question.get("question"),
        "difficulty": question.get("difficulty")
    }

    options = question.get("options")

    if isinstance(options, list):
        safe["options"] = options

    return safe


def sanitize_questions(questions):
    return [
        sanitize_question(
            question,
            index
        )
        for index, question in enumerate(
            questions
        )
        if isinstance(question, dict)
    ]


def get_match_for_user(user_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE
                (
                    player1_id = ?
                    OR player2_id = ?
                )
                AND status NOT IN (
                    'FINISHED',
                    'CANCELLED'
                )
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                user_id
            )
        )

        return cursor.fetchone()

    finally:
        connection.close()


def get_user_by_player_id(player_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                player_id,
                username,
                level,
                xp,
                last_seen
            FROM users
            WHERE player_id = ?
            """,
            (player_id,)
        )

        return cursor.fetchone()

    finally:
        connection.close()


def is_friend(user1_id, user2_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM friends
            WHERE
                (
                    (
                        requester_id = ?
                        AND receiver_id = ?
                    )
                    OR
                    (
                        requester_id = ?
                        AND receiver_id = ?
                    )
                )
                AND status = 'accepted'
            LIMIT 1
            """,
            (
                user1_id,
                user2_id,
                user2_id,
                user1_id
            )
        )

        return cursor.fetchone() is not None

    finally:
        connection.close()


def cleanup_expired_queue(cursor):
    cursor.execute(
        """
        DELETE FROM matchmaking_queue
        WHERE created_at < datetime(
            'now',
            '-10 minutes'
        )
        """
    )


def cleanup_expired_invites(cursor):
    cursor.execute(
        """
        SELECT
            id,
            match_id
        FROM match_invites
        WHERE
            status = 'pending'
            AND created_at < datetime(
                'now',
                '-10 minutes'
            )
        """
    )

    expired = cursor.fetchall()

    for invite in expired:
        cursor.execute(
            """
            UPDATE match_invites
            SET status = 'expired'
            WHERE
                id = ?
                AND status = 'pending'
            """,
            (invite["id"],)
        )

        cursor.execute(
            """
            UPDATE matches
            SET
                status = 'CANCELLED',
                finished_at = ?
            WHERE
                id = ?
                AND status = 'INVITED'
            """,
            (
                now_iso(),
                invite["match_id"]
            )
        )


def cleanup_expired_matches(cursor):
    cursor.execute(
        """
        SELECT
            id,
            started_at
        FROM matches
        WHERE status = 'PLAYING'
        """
    )

    rows = cursor.fetchall()

    for match in rows:
        elapsed = seconds_since(
            match["started_at"]
        )

        if (
            elapsed is not None
            and elapsed >= MATCH_MAX_DURATION_SECONDS
        ):
            cursor.execute(
                """
                UPDATE matches
                SET
                    status = 'FINISHED',
                    finished_at = ?
                WHERE
                    id = ?
                    AND status = 'PLAYING'
                """,
                (
                    now_iso(),
                    match["id"]
                )
            )


def cleanup_matchmaking():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_queue(cursor)
        cleanup_expired_invites(cursor)
        cleanup_expired_matches(cursor)

        connection.commit()

    finally:
        connection.close()


def get_players(cursor, player1_id, player2_id):
    cursor.execute(
        """
        SELECT
            id,
            player_id,
            username,
            level,
            xp,
            last_seen
        FROM users
        WHERE id IN (?, ?)
        """,
        (
            player1_id,
            player2_id
        )
    )

    rows = cursor.fetchall()

    return {
        row["id"]: row
        for row in rows
    }


def format_player(player):
    if not player:
        return None

    return {
        "id": player["id"],
        "player_id": player["player_id"],
        "username": player["username"],
        "level": player["level"],
        "xp": player["xp"],
        "last_seen": player["last_seen"]
    }


def get_opponent_id(match, user_id):
    if user_id == match["player1_id"]:
        return match["player2_id"]

    if user_id == match["player2_id"]:
        return match["player1_id"]

    return None


def is_match_expired(match):
    if match["status"] != "PLAYING":
        return False

    elapsed = seconds_since(
        match["started_at"]
    )

    return (
        elapsed is not None
        and elapsed >= MATCH_MAX_DURATION_SECONDS
    )


def get_question_count(match):
    questions = safe_json_loads(
        match["questions"],
        []
    )

    if not isinstance(questions, list):
        return 0

    return len(questions)


def load_player_answers(match, player_number):
    key = (
        "player1_answers"
        if player_number == 1
        else "player2_answers"
    )

    answers = safe_json_loads(
        match[key],
        {}
    )

    return answers if isinstance(
        answers,
        dict
    ) else {}


def save_player_answers(
    cursor,
    match_id,
    player_number,
    answers
):
    column = (
        "player1_answers"
        if player_number == 1
        else "player2_answers"
    )

    cursor.execute(
        f"""
        UPDATE matches
        SET {column} = ?
        WHERE id = ?
        """,
        (
            safe_json_dumps(answers),
            match_id
        )
    )


def get_player_number(match, user_id):
    if user_id == match["player1_id"]:
        return 1

    if user_id == match["player2_id"]:
        return 2

    return None


def normalize_answer(answer):
    if isinstance(answer, str):
        return answer.strip()

    if isinstance(answer, bool):
        return answer

    if isinstance(answer, (int, float)):
        return answer

    if isinstance(answer, list):
        return [
            normalize_answer(item)
            for item in answer
        ]

    if isinstance(answer, dict):
        return {
            str(key): normalize_answer(value)
            for key, value in answer.items()
        }

    return answer


def check_battle_answer(question, user_answer):
    answer = normalize_answer(user_answer)

    question_type = (
        question.get("question_type")
        or question.get("type")
        or "multiple_choice"
    )

    aliases = {
        "choice": "multiple_choice",
        "mcq": "multiple_choice",
        "multiple-choice": "multiple_choice",
        "input": "short_answer",
        "short": "short_answer",
        "short-answer": "short_answer",
        "tf": "true_false",
        "true-false": "true_false"
    }

    question_type = aliases.get(
        question_type,
        question_type
    )

    correct_answer = question.get(
        "answer"
    )

    if question_type == "multiple_choice":
        return (
            str(answer).strip().lower()
            ==
            str(correct_answer).strip().lower()
        )

    if question_type == "short_answer":
        try:
            from ..ai.engine.solver import equivalent

            return equivalent(
                answer,
                correct_answer
            )
        except Exception:
            return (
                str(answer).strip().lower()
                ==
                str(correct_answer).strip().lower()
            )

    if question_type == "true_false":
        if isinstance(
            correct_answer,
            list
        ):
            if not isinstance(
                answer,
                list
            ):
                answer = [answer]

            normalized_correct = [
                bool(value)
                for value in correct_answer
            ]

            normalized_answer = [
                bool(value)
                for value in answer
            ]

            return (
                normalized_answer
                == normalized_correct
            )

        return bool(answer) == bool(
            correct_answer
        )

    return (
        str(answer).strip().lower()
        ==
        str(correct_answer).strip().lower()
    )


def calculate_player_stats(
    questions,
    answers,
    started_at
):
    correct = 0
    wrong = 0
    blank = 0

    for index in range(
        len(questions)
    ):
        item = answers.get(
            str(index)
        )

        if not isinstance(
            item,
            dict
        ):
            blank += 1
            continue

        if item.get("skipped"):
            blank += 1
            continue

        if item.get("correct"):
            correct += 1
        else:
            wrong += 1

    elapsed = seconds_since(
        started_at
    )

    return {
        "correct": correct,
        "wrong": wrong,
        "blank": blank,
        "time": elapsed or 0
    }


def calculate_winner(match):
    p1_correct = int(
        match["player1_correct"] or 0
    )

    p2_correct = int(
        match["player2_correct"] or 0
    )

    if p1_correct > p2_correct:
        return match["player1_id"]

    if p2_correct > p1_correct:
        return match["player2_id"]

    p1_time = int(
        match["player1_time"] or 0
    )

    p2_time = int(
        match["player2_time"] or 0
    )

    if p1_time < p2_time:
        return match["player1_id"]

    if p2_time < p1_time:
        return match["player2_id"]

    p1_wrong = int(
        match["player1_wrong"] or 0
    )

    p2_wrong = int(
        match["player2_wrong"] or 0
    )

    if p1_wrong < p2_wrong:
        return match["player1_id"]

    if p2_wrong < p1_wrong:
        return match["player2_id"]

    p1_blank = int(
        match["player1_blank"] or 0
    )

    p2_blank = int(
        match["player2_blank"] or 0
    )

    if p1_blank < p2_blank:
        return match["player1_id"]

    if p2_blank < p1_blank:
        return match["player2_id"]

    return None


def finalize_match_if_needed(
    cursor,
    match,
    questions
):
    question_count = len(
        questions
    )

    p1_answers = load_player_answers(
        match,
        1
    )

    p2_answers = load_player_answers(
        match,
        2
    )

    p1_done = len(
        p1_answers
    ) >= question_count

    p2_done = len(
        p2_answers
    ) >= question_count

    if not (
        p1_done
        and p2_done
    ):
        return False, None

    p1_stats = calculate_player_stats(
        questions,
        p1_answers,
        match["started_at"]
    )

    p2_stats = calculate_player_stats(
        questions,
        p2_answers,
        match["started_at"]
    )

    winner_id = calculate_winner(
        {
            **dict(match),
            "player1_correct": p1_stats["correct"],
            "player1_wrong": p1_stats["wrong"],
            "player1_blank": p1_stats["blank"],
            "player1_time": p1_stats["time"],
            "player2_correct": p2_stats["correct"],
            "player2_wrong": p2_stats["wrong"],
            "player2_blank": p2_stats["blank"],
            "player2_time": p2_stats["time"]
        }
    )

    cursor.execute(
        """
        UPDATE matches
        SET
            status = 'FINISHED',

            player1_correct = ?,
            player1_wrong = ?,
            player1_blank = ?,
            player1_time = ?,

            player2_correct = ?,
            player2_wrong = ?,
            player2_blank = ?,
            player2_time = ?,

            winner_id = ?,
            finished_at = ?

        WHERE
            id = ?
            AND status = 'PLAYING'
        """,
        (
            p1_stats["correct"],
            p1_stats["wrong"],
            p1_stats["blank"],
            p1_stats["time"],

            p2_stats["correct"],
            p2_stats["wrong"],
            p2_stats["blank"],
            p2_stats["time"],

            winner_id,
            now_iso(),
            match["id"]
        )
    )

    return True, winner_id


def update_player_stats(
    cursor,
    match,
    questions,
    player_number,
    answers
):
    stats = calculate_player_stats(
        questions,
        answers,
        match["started_at"]
    )

    if player_number == 1:
        cursor.execute(
            """
            UPDATE matches
            SET
                player1_current = ?,
                player1_correct = ?,
                player1_wrong = ?,
                player1_blank = ?,
                player1_time = ?
            WHERE id = ?
            """,
            (
                len(answers),
                stats["correct"],
                stats["wrong"],
                stats["blank"],
                stats["time"],
                match["id"]
            )
        )

    else:
        cursor.execute(
            """
            UPDATE matches
            SET
                player2_current = ?,
                player2_correct = ?,
                player2_wrong = ?,
                player2_blank = ?,
                player2_time = ?
            WHERE id = ?
            """,
            (
                len(answers),
                stats["correct"],
                stats["wrong"],
                stats["blank"],
                stats["time"],
                match["id"]
            )
        )

    return stats


# =========================================================
# RANDOM MATCHMAKING
# =========================================================

@router.post("/random/join")
def join_random_match(
    data: MatchSettings | None = None,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    settings = normalize_settings(
        data or MatchSettings()
    )

    cleanup_matchmaking()

    existing_match = get_match_for_user(
        user["id"]
    )

    if existing_match:
        return {
            "success": True,
            "status": "MATCHED",
            "match_id": existing_match["id"]
        }

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_queue(
            cursor
        )

        cursor.execute(
            """
            DELETE FROM matchmaking_queue
            WHERE user_id = ?
            """,
            (user["id"],)
        )

        cursor.execute(
            """
            SELECT *
            FROM matchmaking_queue
            WHERE user_id != ?
            ORDER BY id ASC
            """,
            (user["id"],)
        )

        queued_players = cursor.fetchall()

        opponent = None
        common_topics = []

        for candidate in queued_players:
            opponent_id = candidate["user_id"]

            opponent_match = get_match_for_user(
                opponent_id
            )

            if opponent_match:
                cursor.execute(
                    """
                    DELETE FROM matchmaking_queue
                    WHERE user_id = ?
                    """,
                    (opponent_id,)
                )
                continue

            candidate_topics = safe_json_loads(
                candidate["topics"],
                []
            )

            candidate_grade = int(
                candidate["grade"]
                or DEFAULT_GRADE
            )

            if candidate_grade != settings["grade"]:
                continue

            common_topics = get_common_topics(
                settings["grade"],
                settings["topics"],
                candidate_topics
            )

            if common_topics:
                opponent = candidate
                break

        if opponent:
            opponent_id = opponent["user_id"]

            opponent_topics = safe_json_loads(
                opponent["topics"],
                []
            )

            opponent_difficulty = (
                opponent["difficulty"]
                or DEFAULT_DIFFICULTY
            )

            opponent_question_type = (
                opponent["question_type"]
                or DEFAULT_QUESTION_TYPE
            )

            difficulty = settings["difficulty"]

            if difficulty != opponent_difficulty:
                difficulty = DEFAULT_DIFFICULTY

            question_type = settings[
                "question_type"
            ]

            if question_type != opponent_question_type:
                question_type = DEFAULT_QUESTION_TYPE

            questions = generate_ai_battle_questions(
                settings["grade"],
                common_topics,
                difficulty,
                question_type
            )

            match_code = (
                "MW-"
                + uuid.uuid4().hex[:10].upper()
            )

            cursor.execute(
                """
                DELETE FROM matchmaking_queue
                WHERE user_id IN (?, ?)
                """,
                (
                    opponent_id,
                    user["id"]
                )
            )

            cursor.execute(
                """
                INSERT INTO matches
                (
                    match_code,
                    player1_id,
                    player2_id,
                    status,
                    questions,
                    topics,
                    grade,
                    difficulty,
                    question_type,
                    player1_answers,
                    player2_answers,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    match_code,
                    opponent_id,
                    user["id"],
                    "STARTING",
                    safe_json_dumps(
                        questions
                    ),
                    safe_json_dumps(
                        common_topics
                    ),
                    settings["grade"],
                    difficulty,
                    question_type,
                    "{}",
                    "{}",
                    now_iso()
                )
            )

            match_id = cursor.lastrowid

            connection.commit()

            return {
                "success": True,
                "status": "MATCHED",
                "match_id": match_id,
                "topics": common_topics,
                "grade": settings["grade"],
                "difficulty": difficulty,
                "question_type": question_type,
                "question_count": len(
                    questions
                )
            }

        cursor.execute(
            """
            INSERT INTO matchmaking_queue
            (
                user_id,
                created_at,
                grade,
                topics,
                difficulty,
                question_type
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET
                created_at = excluded.created_at,
                grade = excluded.grade,
                topics = excluded.topics,
                difficulty = excluded.difficulty,
                question_type = excluded.question_type
            """,
            (
                user["id"],
                now_iso(),
                settings["grade"],
                safe_json_dumps(
                    settings["topics"]
                ),
                settings["difficulty"],
                settings["question_type"]
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "QUEUED",
            "grade": settings["grade"],
            "topics": settings["topics"],
            "difficulty": settings["difficulty"],
            "question_type": settings["question_type"]
        }

    finally:
        connection.close()


# =========================================================
# RANDOM STATUS
# =========================================================

@router.get("/random/status")
def random_match_status(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    cleanup_matchmaking()

    match = get_match_for_user(
        user["id"]
    )

    if match:
        return {
            "success": True,
            "status": "MATCHED",
            "match_id": match["id"],
            "match_status": match["status"]
        }

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                created_at,
                grade,
                topics,
                difficulty,
                question_type
            FROM matchmaking_queue
            WHERE user_id = ?
            """,
            (user["id"],)
        )

        queue = cursor.fetchone()

    finally:
        connection.close()

    if not queue:
        return {
            "success": True,
            "status": "IDLE",
            "waiting": False
        }

    waiting_seconds = seconds_since(
        queue["created_at"]
    )

    return {
        "success": True,
        "status": "QUEUED",
        "waiting": True,
        "waiting_seconds": waiting_seconds or 0,
        "grade": queue["grade"],
        "topics": safe_json_loads(
            queue["topics"],
            []
        ),
        "difficulty": queue["difficulty"],
        "question_type": queue["question_type"]
    }


# =========================================================
# RANDOM CANCEL
# =========================================================

@router.post("/random/cancel")
def cancel_random_match(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM matchmaking_queue
            WHERE user_id = ?
            """,
            (user["id"],)
        )

        connection.commit()

        return {
            "success": True,
            "status": "CANCELLED"
        }

    finally:
        connection.close()


# =========================================================
# FIND PLAYER
# =========================================================

@router.get("/player")
def find_player(
    player_id: str,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    player_id = validate_player_id(
        player_id
    )

    target = get_user_by_player_id(
        player_id
    )

    if not target:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người chơi."
        )

    if target["id"] == user["id"]:
        raise HTTPException(
            status_code=400,
            detail="Bạn không thể đấu với chính mình."
        )

    existing_match = get_match_for_user(
        target["id"]
    )

    return {
        "id": target["id"],
        "player_id": target["player_id"],
        "username": target["username"],
        "level": target["level"],
        "xp": target["xp"],
        "last_seen": target["last_seen"],
        "in_match": existing_match is not None,
        "is_friend": is_friend(
            user["id"],
            target["id"]
        )
    }


# =========================================================
# DIRECT INVITE
# =========================================================

@router.post("/invite")
def invite_player(
    data: InviteRequest,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    settings = normalize_settings(
        data
    )

    target_player_id = validate_player_id(
        data.player_id
    )

    target = get_user_by_player_id(
        target_player_id
    )

    if not target:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người chơi."
        )

    if target["id"] == user["id"]:
        raise HTTPException(
            status_code=400,
            detail="Bạn không thể mời chính mình."
        )

    current_match = get_match_for_user(
        user["id"]
    )

    if current_match:
        raise HTTPException(
            status_code=400,
            detail="Bạn đang ở trong một trận đấu."
        )

    target_match = get_match_for_user(
        target["id"]
    )

    if target_match:
        raise HTTPException(
            status_code=400,
            detail="Người chơi này đang ở trong một trận đấu."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_invites(
            cursor
        )

        cursor.execute(
            """
            SELECT id
            FROM match_invites
            WHERE
                sender_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            LIMIT 1
            """,
            (
                user["id"],
                target["id"]
            )
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Bạn đã gửi lời mời cho người này."
            )

        cursor.execute(
            """
            SELECT id
            FROM match_invites
            WHERE
                sender_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            LIMIT 1
            """,
            (
                target["id"],
                user["id"]
            )
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Người này đã gửi lời mời cho bạn."
            )

        target_topics = get_default_topics(
            settings["grade"]
        )

        common_topics = get_common_topics(
            settings["grade"],
            settings["topics"],
            target_topics
        )

        if not common_topics:
            common_topics = settings["topics"]

        if not common_topics:
            raise HTTPException(
                status_code=400,
                detail="Bạn cần chọn ít nhất một chủ đề để đấu."
            )

        questions = generate_ai_battle_questions(
            settings["grade"],
            common_topics,
            settings["difficulty"],
            settings["question_type"]
        )

        match_code = (
            "MW-"
            + uuid.uuid4().hex[:10].upper()
        )

        cursor.execute(
            """
            INSERT INTO matches
            (
                match_code,
                player1_id,
                player2_id,
                status,
                questions,
                topics,
                grade,
                difficulty,
                question_type,
                player1_answers,
                player2_answers,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_code,
                user["id"],
                target["id"],
                "INVITED",
                safe_json_dumps(
                    questions
                ),
                safe_json_dumps(
                    common_topics
                ),
                settings["grade"],
                settings["difficulty"],
                settings["question_type"],
                "{}",
                "{}",
                now_iso()
            )
        )

        match_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO match_invites
            (
                match_id,
                sender_id,
                receiver_id,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                match_id,
                user["id"],
                target["id"],
                "pending",
                now_iso()
            )
        )

        cursor.execute(
            """
            INSERT INTO notifications
            (
                user_id,
                type,
                title,
                message,
                related_user_id,
                related_id,
                is_read,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                target["id"],
                "pvp_invite",
                "Lời mời đấu PvP",
                f"{user['username']} đã mời bạn đấu PvP.",
                user["id"],
                match_id,
                now_iso()
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "INVITED",
            "match_id": match_id,
            "topics": common_topics,
            "grade": settings["grade"],
            "difficulty": settings["difficulty"],
            "question_type": settings["question_type"],
            "question_count": len(
                questions
            )
        }

    finally:
        connection.close()


# =========================================================
# GET MATCH
# =========================================================

@router.get("/match/{match_id}")
def get_match(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    cleanup_matchmaking()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận đấu."
            )

        if user["id"] not in (
            match["player1_id"],
            match["player2_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu này."
            )

        players = get_players(
            cursor,
            match["player1_id"],
            match["player2_id"]
        )

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            questions = []

        return {
            "id": match["id"],
            "match_code": match["match_code"],
            "status": match["status"],
            "player1_id": match["player1_id"],
            "player2_id": match["player2_id"],

            "players": [
                format_player(
                    players[player_id]
                )
                for player_id in (
                    match["player1_id"],
                    match["player2_id"]
                )
                if player_id in players
            ],

            "topics": safe_json_loads(
                match["topics"],
                []
            ),

            "grade": match["grade"],
            "difficulty": match["difficulty"],
            "question_type": match["question_type"],

            "question_count": len(
                questions
            ),

            "questions": sanitize_questions(
                questions
            ),

            "winner_id": match["winner_id"],
            "created_at": match["created_at"],
            "started_at": match["started_at"],
            "finished_at": match["finished_at"]
        }

    finally:
        connection.close()


# =========================================================
# ACCEPT INVITE
# =========================================================

@router.post("/match/{match_id}/accept")
def accept_invite(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    cleanup_matchmaking()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE
                id = ?
                AND player2_id = ?
                AND status = 'INVITED'
            """,
            (
                match_id,
                user["id"]
            )
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Lời mời không còn tồn tại."
            )

        existing_match = get_match_for_user(
            user["id"]
        )

        if existing_match:
            raise HTTPException(
                status_code=400,
                detail="Bạn đang ở trong một trận đấu khác."
            )

        cursor.execute(
            """
            UPDATE matches
            SET status = 'STARTING'
            WHERE
                id = ?
                AND player2_id = ?
                AND status = 'INVITED'
            """,
            (
                match_id,
                user["id"]
            )
        )

        if cursor.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail="Lời mời vừa được xử lý."
            )

        cursor.execute(
            """
            UPDATE match_invites
            SET status = 'accepted'
            WHERE
                match_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            """,
            (
                match_id,
                user["id"]
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "STARTING",
            "match_id": match_id
        }

    finally:
        connection.close()


# =========================================================
# REJECT INVITE
# =========================================================

@router.post("/match/{match_id}/reject")
def reject_invite(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE
                id = ?
                AND player2_id = ?
                AND status = 'INVITED'
            """,
            (
                match_id,
                user["id"]
            )
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Lời mời không còn tồn tại."
            )

        cursor.execute(
            """
            UPDATE matches
            SET
                status = 'CANCELLED',
                finished_at = ?
            WHERE
                id = ?
                AND status = 'INVITED'
            """,
            (
                now_iso(),
                match_id
            )
        )

        cursor.execute(
            """
            UPDATE match_invites
            SET status = 'rejected'
            WHERE
                match_id = ?
                AND receiver_id = ?
                AND status = 'pending'
            """,
            (
                match_id,
                user["id"]
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "CANCELLED"
        }

    finally:
        connection.close()


# =========================================================
# START MATCH
# =========================================================

@router.post("/match/{match_id}/start")
def start_match(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        if user["id"] not in (
            match["player1_id"],
            match["player2_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        if match["status"] == "PLAYING":
            return {
                "success": True,
                "status": "PLAYING",
                "started_at": match["started_at"]
            }

        if match["status"] != "STARTING":
            raise HTTPException(
                status_code=400,
                detail="Trận đấu chưa thể bắt đầu."
            )

        started_at = now_iso()

        cursor.execute(
            """
            UPDATE matches
            SET
                status = 'PLAYING',
                started_at = ?
            WHERE
                id = ?
                AND status = 'STARTING'
            """,
            (
                started_at,
                match_id
            )
        )

        if cursor.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail="Trận đấu vừa được bắt đầu."
            )

        connection.commit()

        return {
            "success": True,
            "status": "PLAYING",
            "started_at": started_at,
            "duration_seconds": MATCH_MAX_DURATION_SECONDS
        }

    finally:
        connection.close()


# =========================================================
# ANSWER
# =========================================================

@router.post("/match/{match_id}/answer")
def submit_answer(
    match_id: int,
    data: MatchAnswerRequest,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        player_number = get_player_number(
            match,
            user["id"]
        )

        if player_number is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        if match["status"] != "PLAYING":
            raise HTTPException(
                status_code=400,
                detail="Trận đấu chưa ở trạng thái chơi."
            )

        if is_match_expired(match):
            cursor.execute(
                """
                UPDATE matches
                SET
                    status = 'FINISHED',
                    finished_at = ?
                WHERE
                    id = ?
                    AND status = 'PLAYING'
                """,
                (
                    now_iso(),
                    match_id
                )
            )

            connection.commit()

            raise HTTPException(
                status_code=400,
                detail="Trận đấu đã hết thời gian."
            )

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            raise HTTPException(
                status_code=500,
                detail="Bộ câu hỏi không hợp lệ."
            )

        if data.question_index >= len(
            questions
        ):
            raise HTTPException(
                status_code=400,
                detail="Câu hỏi không tồn tại."
            )

        answers = load_player_answers(
            match,
            player_number
        )

        key = str(
            data.question_index
        )

        if key in answers:
            raise HTTPException(
                status_code=409,
                detail="Bạn đã trả lời câu này."
            )

        question = questions[
            data.question_index
        ]

        correct = check_battle_answer(
            question,
            data.answer
        )

        answers[key] = {
            "correct": bool(correct),
            "skipped": False,
            "answered_at": now_iso()
        }

        save_player_answers(
            cursor,
            match_id,
            player_number,
            answers
        )

        stats = update_player_stats(
            cursor,
            match,
            questions,
            player_number,
            answers
        )

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        updated_match = cursor.fetchone()

        finished, winner_id = (
            finalize_match_if_needed(
                cursor,
                updated_match,
                questions
            )
        )

        connection.commit()

        current = len(
            answers
        )

        opponent_number = (
            2
            if player_number == 1
            else 1
        )

        opponent_answers = load_player_answers(
            updated_match,
            opponent_number
        )

        return {
            "success": True,
            "question_index": data.question_index,
            "correct": bool(correct),

            "correct_answer": (
                question.get("answer")
                if not correct
                else None
            ),

            "solution": (
                question.get("solution")
                if not correct
                else None
            ),

            "current": current,
            "total": len(questions),

            "correct_count": stats["correct"],
            "wrong_count": stats["wrong"],
            "blank_count": stats["blank"],

            "opponent_progress": len(
                opponent_answers
            ),

            "status": (
                "FINISHED"
                if finished
                else "PLAYING"
            ),

            "winner_id": winner_id
        }

    finally:
        connection.close()


# =========================================================
# SKIP
# =========================================================

@router.post("/match/{match_id}/skip")
def skip_question(
    match_id: int,
    data: MatchSkipRequest,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        player_number = get_player_number(
            match,
            user["id"]
        )

        if player_number is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        if match["status"] != "PLAYING":
            raise HTTPException(
                status_code=400,
                detail="Trận đấu chưa ở trạng thái chơi."
            )

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            raise HTTPException(
                status_code=500,
                detail="Bộ câu hỏi không hợp lệ."
            )

        if data.question_index >= len(
            questions
        ):
            raise HTTPException(
                status_code=400,
                detail="Câu hỏi không tồn tại."
            )

        answers = load_player_answers(
            match,
            player_number
        )

        key = str(
            data.question_index
        )

        if key in answers:
            raise HTTPException(
                status_code=409,
                detail="Bạn đã xử lý câu này."
            )

        answers[key] = {
            "correct": False,
            "skipped": True,
            "answered_at": now_iso()
        }

        save_player_answers(
            cursor,
            match_id,
            player_number,
            answers
        )

        stats = update_player_stats(
            cursor,
            match,
            questions,
            player_number,
            answers
        )

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        updated_match = cursor.fetchone()

        finished, winner_id = (
            finalize_match_if_needed(
                cursor,
                updated_match,
                questions
            )
        )

        connection.commit()

        opponent_number = (
            2
            if player_number == 1
            else 1
        )

        opponent_answers = load_player_answers(
            updated_match,
            opponent_number
        )

        return {
            "success": True,
            "question_index": data.question_index,
            "skipped": True,

            "current": len(
                answers
            ),

            "total": len(
                questions
            ),

            "correct_count": stats["correct"],
            "wrong_count": stats["wrong"],
            "blank_count": stats["blank"],

            "opponent_progress": len(
                opponent_answers
            ),

            "status": (
                "FINISHED"
                if finished
                else "PLAYING"
            ),

            "winner_id": winner_id
        }

    finally:
        connection.close()


# =========================================================
# PROGRESS
# =========================================================

@router.get("/match/{match_id}/progress")
def get_match_progress(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        player_number = get_player_number(
            match,
            user["id"]
        )

        if player_number is None:
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận đấu."
            )

        questions = safe_json_loads(
            match["questions"],
            []
        )

        if not isinstance(
            questions,
            list
        ):
            questions = []

        own_answers = load_player_answers(
            match,
            player_number
        )

        opponent_number = (
            2
            if player_number == 1
            else 1
        )

        opponent_answers = load_player_answers(
            match,
            opponent_number
        )

        own_stats = calculate_player_stats(
            questions,
            own_answers,
            match["started_at"]
        )

        opponent_stats = calculate_player_stats(
            questions,
            opponent_answers,
            match["started_at"]
        )

        elapsed = seconds_since(
            match["started_at"]
        ) or 0

        remaining = max(
            0,
            MATCH_MAX_DURATION_SECONDS
            - elapsed
        )

        return {
            "success": True,
            "match_id": match_id,
            "status": match["status"],

            "total": len(
                questions
            ),

            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,

            "you": {
                "current": len(
                    own_answers
                ),
                **own_stats
            },

            "opponent": {
                "current": len(
                    opponent_answers
                ),
                **opponent_stats
            },

            "winner_id": match["winner_id"]
        }

    finally:
        connection.close()


# =========================================================
# RESULT
# =========================================================

@router.get("/match/{match_id}/result")
def get_match_result(
    match_id: int,
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    validate_match_id(
        match_id
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matches
            WHERE id = ?
            """,
            (match_id,)
        )

        match = cursor.fetchone()

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy trận."
            )

        if user["id"] not in (
            match["player1_id"],
            match["player2_id"]
        ):
            raise HTTPException(
                status_code=403,
                detail="Bạn không thuộc trận."
            )

        return {
            "success": True,
            "match_id": match["id"],
            "status": match["status"],
            "winner_id": match["winner_id"],

            "topics": safe_json_loads(
                match["topics"],
                []
            ),

            "grade": match["grade"],
            "difficulty": match["difficulty"],
            "question_type": match["question_type"],

            "player1": {
                "user_id": match["player1_id"],
                "correct": match["player1_correct"],
                "wrong": match["player1_wrong"],
                "blank": match["player1_blank"],
                "time": match["player1_time"]
            },

            "player2": {
                "user_id": match["player2_id"],
                "correct": match["player2_correct"],
                "wrong": match["player2_wrong"],
                "blank": match["player2_blank"],
                "time": match["player2_time"]
            },

            "is_finished": (
                match["status"]
                == "FINISHED"
            ),

            "is_draw": (
                match["status"]
                == "FINISHED"
                and match["winner_id"]
                is None
            )
        }

    finally:
        connection.close()


# =========================================================
# CURRENT MATCH
# =========================================================

@router.get("/current")
def current_match(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    cleanup_matchmaking()

    match = get_match_for_user(
        user["id"]
    )

    if not match:
        return {
            "success": True,
            "match": None
        }

    return {
        "success": True,
        "match": {
            "id": match["id"],
            "match_code": match["match_code"],
            "status": match["status"],
            "player1_id": match["player1_id"],
            "player2_id": match["player2_id"],
            "winner_id": match["winner_id"],

            "topics": safe_json_loads(
                match["topics"],
                []
            ),

            "grade": match["grade"],
            "difficulty": match["difficulty"],
            "question_type": match["question_type"],

            "created_at": match["created_at"],
            "started_at": match["started_at"],
            "finished_at": match["finished_at"]
        }
    }


# =========================================================
# PENDING INVITES
# =========================================================

@router.get("/invites")
def get_pending_invites(
    authorization: str = Header(default=None)
):
    user = get_user(
        authorization
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cleanup_expired_invites(
            cursor
        )

        cursor.execute(
            """
            SELECT
                mi.id,
                mi.match_id,
                mi.sender_id,
                mi.receiver_id,
                mi.status,
                mi.created_at,

                u.player_id,
                u.username,
                u.level,
                u.xp

            FROM match_invites mi

            JOIN users u
                ON u.id = mi.sender_id

            WHERE
                mi.receiver_id = ?
                AND mi.status = 'pending'

            ORDER BY mi.id DESC
            """,
            (user["id"],)
        )

        rows = cursor.fetchall()

        connection.commit()

        invites = []

        for row in rows:
            invites.append(
                {
                    "id": row["id"],
                    "match_id": row["match_id"],
                    "status": row["status"],
                    "created_at": row["created_at"],

                    "sender": {
                        "id": row["sender_id"],
                        "player_id": row["player_id"],
                        "username": row["username"],
                        "level": row["level"],
                        "xp": row["xp"]
                    }
                }
            )

        return {
            "success": True,
            "invites": invites,
            "count": len(invites)
        }

    finally:
        connection.close()